# Uses HuggingFace's Whisper and torch for streaming STT
from transformers import pipeline
import torch
import asyncio

pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large", device=0 if torch.cuda.is_available() else -1)

async def transcribe_audio_stream(audio_bytes):
    # Simulate streaming with chunked inference (replace to real streaming for production)
    result = pipe(audio_bytes)
    text = result["text"]
    for token in text.split():  # Sends each word (for demo, you can stream fragments)
        await asyncio.sleep(0.01)
        yield token
