"""
Test Voice Agent Backend

Tests for STT, TTS, audio processing, and WebSocket functionality.
"""

import pytest
import asyncio
import base64
import os
from pathlib import Path

# Set test environment variables
os.environ['VOICE_ENABLED'] = 'true'
os.environ['MODEL_CACHE_DIR'] = 'backend/models'
os.environ['WHISPER_MODEL'] = 'openai/whisper-tiny'  # Use tiny model for faster tests
os.environ['WHISPER_DEVICE'] = 'cpu'
os.environ['WHISPER_COMPUTE_TYPE'] = 'int8'


class TestAudioUtils:
    """Test audio processing utilities."""
    
    def test_base64_encoding(self):
        """Test base64 encoding/decoding."""
        from backend.voice.audio_utils import AudioProcessor
        
        processor = AudioProcessor()
        test_data = b"test audio data"
        
        # Encode
        encoded = processor.bytes_to_base64(test_data)
        assert isinstance(encoded, str)
        
        # Decode
        decoded = processor.base64_to_bytes(encoded)
        assert decoded == test_data
    
    def test_audio_buffer(self):
        """Test audio buffering."""
        from backend.voice.audio_utils import AudioBuffer
        
        buffer = AudioBuffer(chunk_duration=3.0, max_duration=60.0)
        
        # Initially empty
        assert buffer.get_chunk_count() == 0
        assert not buffer.is_ready()
        
        # Add some data
        buffer.add(b"chunk1")
        buffer.add(b"chunk2")
        
        assert buffer.get_chunk_count() == 2
        
        # Clear
        buffer.clear()
        assert buffer.get_chunk_count() == 0


class TestModelManager:
    """Test model manager."""
    
    def test_model_info(self):
        """Test getting model info."""
        from backend.voice.model_manager import ModelManager
        
        info = ModelManager.get_model_info()
        
        assert 'voice_enabled' in info
        assert 'models_loaded' in info
        assert 'cache_dir' in info
        assert 'config' in info
    
    def test_cache_dir_creation(self):
        """Test cache directory creation."""
        from backend.voice.model_manager import ModelManager
        
        cache_dir = ModelManager.get_cache_dir()
        assert cache_dir.exists()
        assert cache_dir.is_dir()


class TestWhisperSTT:
    """Test Whisper STT functionality."""
    
    @pytest.mark.skipif(
        not os.path.exists("backend/models"),
        reason="Models not downloaded yet"
    )
    def test_model_loading(self):
        """Test Whisper model loading."""
        from backend.voice.stt import WhisperSTT
        
        # This will download the model on first run
        stt = WhisperSTT(
            model_name="openai/whisper-tiny",
            cache_dir="backend/models",
            device="cpu",
            compute_type="int8"
        )
        
        assert stt.model is not None
        
        # Test model info
        info = stt.get_model_info()
        assert info['loaded'] is True
        assert 'whisper-tiny' in info['model_name']
    
    def test_supported_languages(self):
        """Test getting supported languages."""
        from backend.voice.stt import WhisperSTT
        
        stt = WhisperSTT(
            model_name="openai/whisper-tiny",
            cache_dir="backend/models"
        )
        
        languages = stt.get_supported_languages()
        assert isinstance(languages, list)
        assert 'en' in languages
        assert len(languages) > 50  # Whisper supports 99 languages


class TestCoquiTTS:
    """Test Coqui TTS functionality."""
    
    @pytest.mark.skipif(
        not os.path.exists("backend/models"),
        reason="Models not downloaded yet"
    )
    def test_model_loading(self):
        """Test TTS model loading."""
        from backend.voice.tts import CoquiTTS
        
        # This will download the model on first run
        tts = CoquiTTS(
            model_name="tts_models/en/ljspeech/tacotron2-DDC",
            cache_dir="backend/models"
        )
        
        assert tts.tts is not None
        
        # Test model info
        info = tts.get_model_info()
        assert info['loaded'] is True
    
    def test_list_models(self):
        """Test listing available TTS models."""
        from backend.voice.tts import CoquiTTS
        
        models = CoquiTTS.list_available_models()
        assert isinstance(models, list)
        # Should have many models available
        assert len(models) > 0


class TestVoiceIntegration:
    """Integration tests for voice functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.path.exists("backend/models"),
        reason="Models not downloaded yet"
    )
    async def test_stt_transcription(self):
        """Test end-to-end STT transcription."""
        from backend.voice.model_manager import ModelManager
        
        # Get STT model
        stt = ModelManager.get_stt_model()
        if not stt:
            pytest.skip("STT model not available")
        
        # Create a simple test audio file (would need actual audio in real test)
        # For now, just test the interface
        assert hasattr(stt, 'transcribe')
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.path.exists("backend/models"),
        reason="Models not downloaded yet"
    )
    async def test_tts_synthesis(self):
        """Test end-to-end TTS synthesis."""
        from backend.voice.model_manager import ModelManager
        
        # Get TTS model
        tts = ModelManager.get_tts_model()
        if not tts:
            pytest.skip("TTS model not available")
        
        # Test synthesis
        text = "Hello, this is a test."
        audio_bytes = await tts.synthesize(text)
        
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0


def test_voice_enabled():
    """Test voice enabled check."""
    from backend.voice.model_manager import ModelManager
    
    assert ModelManager.is_voice_enabled() is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
