import torch
import torch.nn.functional as F
import torchaudio
import numpy as np
import pandas as pd

from torchaudio.functional import resample
from transformers import Wav2Vec2FeatureExtractor, UniSpeechSatForXVector
from pathlib import Path
from tqdm import tqdm

# Python QDrant client wrapper for REST API generated by OpenAPI
from qdrant_client import QdrantClient


# set the paths and names
model_name = 'microsoft/unispeech-sat-base-plus-sv'
dataset_path = Path('voxceleba1')
id_to_name_path = Path('id_to_name.csv')
COLLECTION_NAME = 'vox_celeba'

# Load the model
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
model = UniSpeechSatForXVector.from_pretrained(model_name).cuda()
model.eval()
target_sampling_rate = feature_extractor.sampling_rate


# connect to QDrant & create collection
client = QdrantClient(host="localhost", port=6333)
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vector_size=512  # our model produces 512-d embeddings
)

# Load mapping speaker id -> meta data
meta_data = pd.read_csv(id_to_name_path)
meta_data = meta_data.set_index('VoxCeleb1 ID').T.to_dict()


def get_embedding(input_audio: torch.Tensor) -> np.ndarray:
    inputs = feature_extractor(
        input_audio,
        sampling_rate=16000,
        return_tensors="pt"
    )  # pad and covert to tensor
    input_values = inputs.input_values.cuda()
    with torch.no_grad():
        embedding = model(input_values).embeddings
    # normalize the vectors because we want to use cosine similarity
    embedding = F.normalize(embedding, dim=-1)
    return embedding.squeeze(0).cpu().numpy()  # qdrant accepts numpy arrays


# traverse over the dataset folder
vec_idx = 0
total_vectors = []
total_payloads = []
for speaker_id in tqdm(list(dataset_path.iterdir())):
    for video_link in speaker_id.iterdir():
        for utterance in video_link.iterdir():
            # load the audio
            audio, sampling_rate = torchaudio.load(utterance)
            audio = resample(audio, sampling_rate, target_sampling_rate)
            audio = audio.squeeze(0)

            # obtain the embedding
            embedding = get_embedding(audio)

            # save the embedding and the payload into a list
            spkr_id = speaker_id.name
            payload_data = {
                'speaker_id': spkr_id,
                'video_link': video_link.name,
                'utterance': utterance.name,
                'full_name': meta_data[spkr_id]['VGGFace1 ID'],
                'gender': meta_data[spkr_id]['Gender'],
                'nationality': meta_data[spkr_id]['Nationality']
            }
            total_vectors.append(embedding)
            total_payloads.append(payload_data)

# create a dense np.ndarray from the list
total_vectors = np.array(total_vectors)

# Upload data to the QDrant collection
client.upload_collection(
    collection_name=COLLECTION_NAME,
    vectors=total_vectors,
    payload=total_payloads,
    ids=None,  # Let client auto-assign sequential ids
    parallel=2
)
