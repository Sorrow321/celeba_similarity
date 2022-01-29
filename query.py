import torch
import torch.nn.functional as F
import torchaudio
from torchaudio.functional import resample
from transformers import Wav2Vec2FeatureExtractor, UniSpeechSatForXVector
from pathlib import Path


model_name = 'microsoft/unispeech-sat-base-plus-sv'
dataset_path = Path('voxceleba1')
COLLECTION_NAME = 'vox_celeba'

# Load the model
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


def get_embedding_from_file(path: Path) -> torch.Tensor:
    audio, sampling_rate = torchaudio.load(path)
    audio = resample(audio, sampling_rate, target_sampling_rate)
    audio = audio.squeeze(0)
    embedding = get_embedding(audio)
    return embedding
