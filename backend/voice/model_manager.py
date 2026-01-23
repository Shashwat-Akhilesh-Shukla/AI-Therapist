"""
Model Manager for Voice Agent

Handles lazy loading, caching, and lifecycle management of STT and TTS models.
Implements singleton pattern to ensure only one instance of each model is loaded.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Centralized manager for STT and TTS models.
    
    Features:
    - Lazy loading: models only load on first use
    - Singleton pattern: one instance per model type
    - Automatic caching to disk
    - Environment-based configuration
    """
    
    _instance = None
    _stt_model = None
    _tts_model = None
    _models_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_cache_dir(cls) -> Path:
        """Get the model cache directory from environment or use default."""
        cache_dir = os.getenv("MODEL_CACHE_DIR", "backend/models")
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    
    @classmethod
    def is_voice_enabled(cls) -> bool:
        """Check if voice functionality is enabled."""
        return os.getenv("VOICE_ENABLED", "true").lower() == "true"
    
    @classmethod
    def get_stt_model(cls):
        """
        Get or initialize the STT model.
        
        Returns:
            WhisperSTT: Initialized Whisper model instance
        """
        if not cls.is_voice_enabled():
            logger.warning("Voice functionality is disabled (VOICE_ENABLED=false)")
            return None
        
        if cls._stt_model is None:
            try:
                from .stt import WhisperSTT
                
                model_name = os.getenv("WHISPER_MODEL", "openai/whisper-medium")
                device = os.getenv("WHISPER_DEVICE", "cpu")
                compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
                
                logger.info(f"Loading Whisper STT model: {model_name} on {device} with {compute_type}")
                
                cls._stt_model = WhisperSTT(
                    model_name=model_name,
                    cache_dir=str(cls.get_cache_dir()),
                    device=device,
                    compute_type=compute_type
                )
                
                logger.info("✓ Whisper STT model loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load STT model: {e}")
                cls._stt_model = None
                raise
        
        return cls._stt_model
    
    @classmethod
    def get_tts_model(cls):
        """
        Get or initialize the TTS model.
        
        Returns:
            CoquiTTS: Initialized Coqui TTS model instance
        """
        if not cls.is_voice_enabled():
            logger.warning("Voice functionality is disabled (VOICE_ENABLED=false)")
            return None
        
        if cls._tts_model is None:
            try:
                from .tts import CoquiTTS
                
                model_name = os.getenv(
                    "COQUI_MODEL", 
                    "tts_models/en/ljspeech/tacotron2-DDC"
                )
                
                logger.info(f"Loading Coqui TTS model: {model_name}")
                
                cls._tts_model = CoquiTTS(
                    model_name=model_name,
                    cache_dir=str(cls.get_cache_dir())
                )
                
                logger.info("✓ Coqui TTS model loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load TTS model: {e}")
                cls._tts_model = None
                raise
        
        return cls._tts_model
    
    @classmethod
    def preload_models(cls):
        """
        Preload both STT and TTS models.
        
        Useful for warming up the system before handling requests.
        """
        if not cls.is_voice_enabled():
            logger.info("Voice functionality disabled, skipping model preload")
            return
        
        try:
            logger.info("Preloading voice models...")
            cls.get_stt_model()
            cls.get_tts_model()
            cls._models_loaded = True
            logger.info("✓ All voice models preloaded successfully")
        except Exception as e:
            logger.error(f"Failed to preload models: {e}")
            raise
    
    @classmethod
    def unload_models(cls):
        """
        Unload models to free memory.
        
        Useful for cleanup or when voice functionality is no longer needed.
        """
        if cls._stt_model is not None:
            del cls._stt_model
            cls._stt_model = None
            logger.info("STT model unloaded")
        
        if cls._tts_model is not None:
            del cls._tts_model
            cls._tts_model = None
            logger.info("TTS model unloaded")
        
        cls._models_loaded = False
    
    @classmethod
    def get_model_info(cls) -> dict:
        """
        Get information about loaded models.
        
        Returns:
            dict: Model status and configuration
        """
        return {
            "voice_enabled": cls.is_voice_enabled(),
            "models_loaded": cls._models_loaded,
            "stt_loaded": cls._stt_model is not None,
            "tts_loaded": cls._tts_model is not None,
            "cache_dir": str(cls.get_cache_dir()),
            "config": {
                "whisper_model": os.getenv("WHISPER_MODEL", "openai/whisper-medium"),
                "whisper_device": os.getenv("WHISPER_DEVICE", "cpu"),
                "whisper_compute_type": os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
                "coqui_model": os.getenv("COQUI_MODEL", "tts_models/en/ljspeech/tacotron2-DDC"),
            }
        }
