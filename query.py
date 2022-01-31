import torch
import torch.nn.functional as F
import torchaudio
import numpy as np

from torchaudio.functional import resample
from transformers import Wav2Vec2FeatureExtractor, UniSpeechSatForXVector
from pathlib import Path


# Set the paths and names
model_name = 'microsoft/unispeech-sat-base-plus-sv'
dataset_path = Path('voxceleba1')

# Load the model
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
model = UniSpeechSatForXVector.from_pretrained(model_name)
model.eval()
target_sampling_rate = feature_extractor.sampling_rate


def get_embedding(input_audio: torch.Tensor) -> np.ndarray:
    inputs = feature_extractor(
        input_audio,
        sampling_rate=16000,
        return_tensors="pt"
    )  # pad and covert to tensor
    input_values = inputs.input_values
    with torch.no_grad():
        embedding = model(input_values).embeddings
    # normalize the vectors because we want to use cosine similarity
    embedding = F.normalize(embedding, dim=-1)
    return embedding.squeeze(0).cpu().numpy()  # qdrant accepts numpy arrays


def get_embedding_from_file(path: Path) -> np.ndarray:
    audio, sampling_rate = torchaudio.load(path)
    audio = resample(audio, sampling_rate, target_sampling_rate)
    audio = audio.squeeze(0)
    embedding = get_embedding(audio)
    return embedding
