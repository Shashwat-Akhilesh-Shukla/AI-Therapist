# Uses Coqui TTS for nearly real-time audio streaming (simplified here)
from TTS.api import TTS
import asyncio

tts_model = TTS(model_name="tts_models/en/vctk/vits").to("cuda")

async def tts_stream(text):
    # Generate audio file quickly (can chunk for real streaming)
    tts_model.tts_to_file(text, file_path="output.wav")
    with open("output.wav", "rb") as f:
        data = f.read(1024)
        while data:
            await asyncio.sleep(0.01)
            yield data
            data = f.read(1024)
