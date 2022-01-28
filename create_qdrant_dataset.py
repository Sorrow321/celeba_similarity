import requests
import torch
import torch.nn.functional as F
import torchaudio
from torchaudio.functional import resample
from transformers import Wav2Vec2FeatureExtractor, UniSpeechSatForXVector
from pathlib import Path
from tqdm import tqdm
import numpy as np


qdrant_address = 'http://localhost:6333/collections/test_collection?wait=true'
model_name = 'microsoft/unispeech-sat-base-plus-sv'
dataset_path = Path('voxceleba1')

feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
model = UniSpeechSatForXVector.from_pretrained(model_name).cuda()
model.eval()
target_sampling_rate = feature_extractor.sampling_rate


def get_embedding(input_audio: torch.Tensor) -> torch.Tensor:
    inputs = feature_extractor(
        input_audio,
        sampling_rate=16000,
        return_tensors="pt"
    )
    input_values = inputs.input_values.cuda()
    with torch.no_grad():
        embedding = model(input_values).embeddings
    embedding = F.normalize(embedding, dim=-1)
    return embedding.squeeze(0).cpu().numpy()


# traverse over the dataset folder
vec_idx = 0
for speaker_id in tqdm(list(dataset_path.iterdir())):
    for video_link in speaker_id.iterdir():
        for utterance in video_link.iterdir():
            # load the audio
            audio, sampling_rate = torchaudio.load(utterance)
            audio = resample(audio, sampling_rate, target_sampling_rate)
            audio = audio.squeeze(0)

            # obtain the embedding
            embedding = get_embedding(audio)

            # load the embedding into QDrant
            data = {
                'upsert_points': {
                    'points': [
                        {
                            'id': vec_idx,
                            'vector': np.array2string(embedding, separator=','),
                            'payload':
                            {
                                'speaker_id': str(speaker_id),
                                'video_link': str(video_link),
                                'utterance': str(utterance)
                            }
                        }
                    ]
                }
            }
            r = requests.post(qdrant_address, json=data)

            vec_idx += 1
