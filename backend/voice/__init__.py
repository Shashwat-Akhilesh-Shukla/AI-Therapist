"""
Voice Agent Module

Provides speech-to-text (STT) and text-to-speech (TTS) functionality
for real-time voice conversations.
"""

from .stt import WhisperSTT
from .tts import CoquiTTS
from .model_manager import ModelManager
from .audio_utils import AudioProcessor, AudioBuffer

__all__ = [
    'WhisperSTT',
    'CoquiTTS',
    'ModelManager',
    'AudioProcessor',
    'AudioBuffer'
]
