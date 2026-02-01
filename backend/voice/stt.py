"""
Speech-to-Text (STT) using Whisper

Implements optimized Whisper-based transcription with caching,
latency optimization, and error handling.
"""

import os
import io
import logging
import time
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class WhisperSTT:
    """
    Whisper-based Speech-to-Text engine.
    
    Features:
    - Automatic model caching
    - Optimized inference with faster-whisper
    - Support for CPU and GPU
    - Configurable compute types (int8, float16)
    """
    
    def __init__(
        self,
        model_name: str = "openai/whisper-medium",
        cache_dir: str = "backend/models",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Initialize Whisper STT model.
        
        Args:
            model_name: HuggingFace model identifier or local path
            cache_dir: Directory for model caching
            device: Device to use ('cpu' or 'cuda')
            compute_type: Compute type ('int8', 'float16', 'float32')
        """
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.device = device
        self.compute_type = compute_type
        self.model = None
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model with caching."""
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Whisper model: {self.model_name}")
            logger.info(f"Device: {self.device}, Compute type: {self.compute_type}")
            logger.info(f"Cache directory: {self.cache_dir}")
            
            # Extract model size from model name
            # e.g., "openai/whisper-medium" -> "medium"
            if "/" in self.model_name:
                model_size = self.model_name.split("/")[-1].replace("whisper-", "")
            else:
                model_size = self.model_name
            
            # Load model with faster-whisper
            self.model = WhisperModel(
                model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=str(self.cache_dir)
            )
            
            logger.info("✓ Whisper model loaded successfully")
            
        except ImportError:
            logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def transcribe(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            audio_bytes: Audio data (WAV format, 16kHz recommended)
            language: Language code (e.g., 'en', 'es'). Auto-detect if None.
            task: 'transcribe' or 'translate' (translate to English)
        
        Returns:
            dict: {
                'text': str,
                'language': str,
                'duration': float,
                'segments': list
            }
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        start_time = time.time()
        
        try:
            # Save audio to temporary file (faster-whisper requires file path)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_bytes)
            
            try:
                # Transcribe
                segments, info = self.model.transcribe(
                    temp_path,
                    language=language,
                    task=task,
                    beam_size=5,
                    vad_filter=True,  # Voice Activity Detection to skip silence
                    vad_parameters=dict(
                        min_silence_duration_ms=500,
                        speech_pad_ms=200
                    )
                )
                
                # Collect segments
                segment_list = []
                full_text = ""
                
                for segment in segments:
                    segment_dict = {
                        'start': segment.start,
                        'end': segment.end,
                        'text': segment.text.strip()
                    }
                    segment_list.append(segment_dict)
                    full_text += segment.text.strip() + " "
                
                full_text = full_text.strip()
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                result = {
                    'text': full_text,
                    'language': info.language if hasattr(info, 'language') else 'unknown',
                    'duration': info.duration if hasattr(info, 'duration') else 0.0,
                    'processing_time': processing_time,
                    'segments': segment_list
                }
                
                logger.info(f"Transcription complete: '{full_text[:50]}...' ({processing_time:.2f}s)")
                
                return result
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
        
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def transcribe_sync(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Synchronous transcription for use with thread pool executor.
        
        Args:
            audio_bytes: Audio data (WAV format, 16kHz recommended)
            language: Language code (e.g., 'en'). Auto-detect if None.
            task: 'transcribe' or 'translate'
        
        Returns:
            dict: Transcription result with 'text', 'language', 'duration', 'segments'
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        start_time = time.time()
        
        try:
            # Save audio to temporary file (faster-whisper requires file path)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_bytes)
            
            try:
                # Transcribe
                segments, info = self.model.transcribe(
                    temp_path,
                    language=language,
                    task=task,
                    beam_size=5,
                    vad_filter=True,
                    vad_parameters=dict(
                        min_silence_duration_ms=500,
                        speech_pad_ms=200
                    )
                )
                
                # Collect segments
                segment_list = []
                full_text = ""
                
                for segment in segments:
                    segment_dict = {
                        'start': segment.start,
                        'end': segment.end,
                        'text': segment.text.strip()
                    }
                    segment_list.append(segment_dict)
                    full_text += segment.text.strip() + " "
                
                full_text = full_text.strip()
                processing_time = time.time() - start_time
                
                result = {
                    'text': full_text,
                    'language': info.language if hasattr(info, 'language') else 'unknown',
                    'duration': info.duration if hasattr(info, 'duration') else 0.0,
                    'processing_time': processing_time,
                    'segments': segment_list
                }
                
                logger.info(f"[SYNC] Transcription: '{full_text[:50]}...' ({processing_time:.2f}s)")
                return result
                
            finally:
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
        
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
        Returns:
            list: Language codes
        """
        # Whisper supports 99 languages
        return [
            'en', 'zh', 'de', 'es', 'ru', 'ko', 'fr', 'ja', 'pt', 'tr',
            'pl', 'ca', 'nl', 'ar', 'sv', 'it', 'id', 'hi', 'fi', 'vi',
            'he', 'uk', 'el', 'ms', 'cs', 'ro', 'da', 'hu', 'ta', 'no',
            'th', 'ur', 'hr', 'bg', 'lt', 'la', 'mi', 'ml', 'cy', 'sk',
            'te', 'fa', 'lv', 'bn', 'sr', 'az', 'sl', 'kn', 'et', 'mk',
            'br', 'eu', 'is', 'hy', 'ne', 'mn', 'bs', 'kk', 'sq', 'sw',
            'gl', 'mr', 'pa', 'si', 'km', 'sn', 'yo', 'so', 'af', 'oc',
            'ka', 'be', 'tg', 'sd', 'gu', 'am', 'yi', 'lo', 'uz', 'fo',
            'ht', 'ps', 'tk', 'nn', 'mt', 'sa', 'lb', 'my', 'bo', 'tl',
            'mg', 'as', 'tt', 'haw', 'ln', 'ha', 'ba', 'jw', 'su'
        ]
    
    def get_model_info(self) -> dict:
        """
        Get model information.
        
        Returns:
            dict: Model metadata
        """
        return {
            'model_name': self.model_name,
            'device': self.device,
            'compute_type': self.compute_type,
            'cache_dir': str(self.cache_dir),
            'loaded': self.model is not None
        }
