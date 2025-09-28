import os
import base64
import json
import logging
from typing import Optional
import tempfile

class SpeechService:
    """Service for speech-to-text and text-to-speech functionality"""
    
    def __init__(self):
        # Try both API key variations
        self.api_key = os.environ.get("GOOGLE_CLOUD_API_KEY") or os.environ.get("GEMINI_API_KEY", "default_key")
        self.tts_api_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        self.stt_api_url = "https://speech.googleapis.com/v1/speech:recognize"
    
    def text_to_speech(self, text: str, language_code: str = "en-US") -> bytes:
        """Convert text to speech using Google Cloud Text-to-Speech API"""
        try:
            import requests
            
            # Prepare the request payload for more natural voice
            payload = {
                "input": {"text": text},
                "voice": {
                    "languageCode": language_code,
                    "name": "en-US-Neural2-F",  # Neural voice for more natural sound
                    "ssmlGender": "FEMALE"
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": 0.95,  # Slightly slower for clarity
                    "pitch": 0.5,          # Slightly higher pitch for friendliness
                    "volumeGainDb": 0.0,
                    "sampleRateHertz": 24000,
                    "effectsProfileId": ["telephony-class-application"]
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key
            }
            
            response = requests.post(
                f"{self.tts_api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                audio_content = result.get("audioContent", "")
                if audio_content:
                    return base64.b64decode(audio_content)
                else:
                    logging.error("TTS API returned empty audio content")
                    return b''
            else:
                logging.error(f"TTS API error: {response.status_code} - {response.text}")
                return b''
                
        except Exception as e:
            logging.error(f"Text-to-speech error: {e}")
            return b''
    
    def speech_to_text(self, audio_data: bytes, language_code: str = "en-US") -> Optional[str]:
        """Convert speech to text using Google Cloud Speech-to-Text API"""
        try:
            import requests
            
            # Detect audio format and configure accordingly
            audio_format = self._detect_audio_format(audio_data)
            encoding_config = self._get_encoding_config(audio_format)
            
            if not encoding_config:
                logging.error(f"Unsupported audio format: {audio_format}")
                return None
            
            # Encode audio data
            audio_content = base64.b64encode(audio_data).decode('utf-8')
            
            # Prepare the request payload with enhanced recognition
            payload = {
                "config": {
                    "encoding": encoding_config["encoding"],
                    "sampleRateHertz": encoding_config["sample_rate"],
                    "languageCode": language_code,
                    "enableAutomaticPunctuation": True,
                    "enableWordTimeOffsets": False,
                    "enableSpeakerDiarization": False,
                    "model": "latest_long",
                    "useEnhanced": True,
                    "alternativeLanguageCodes": ["en-GB", "en-AU"]  # Additional English variants
                },
                "audio": {
                    "content": audio_content
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key
            }
            
            response = requests.post(
                f"{self.stt_api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                results = result.get("results", [])
                if results and results[0].get("alternatives"):
                    transcript = results[0]["alternatives"][0]["transcript"]
                    confidence = results[0]["alternatives"][0].get("confidence", 0.0)
                    
                    # Log confidence for debugging
                    logging.info(f"Speech recognition confidence: {confidence}")
                    
                    return transcript
                return None
            else:
                logging.error(f"STT API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Speech-to-text error: {e}")
            return None
    
    def validate_api_key(self) -> bool:
        """Validate if the API key is configured and working"""
        if not self.api_key or self.api_key == "default_key":
            return False
        
        try:
            # Try a simple TTS request to validate
            test_audio = self.text_to_speech("Hello")
            return len(test_audio) > 0
        except:
            return False
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages for speech services"""
        return [
            {"code": "en-US", "name": "English (US)"},
            {"code": "en-GB", "name": "English (UK)"},
            {"code": "en-AU", "name": "English (Australia)"},
            {"code": "es-ES", "name": "Spanish (Spain)"},
            {"code": "es-US", "name": "Spanish (US)"},
            {"code": "fr-FR", "name": "French (France)"},
            {"code": "fr-CA", "name": "French (Canada)"},
            {"code": "de-DE", "name": "German"},
            {"code": "it-IT", "name": "Italian"},
            {"code": "pt-BR", "name": "Portuguese (Brazil)"},
            {"code": "ja-JP", "name": "Japanese"},
            {"code": "ko-KR", "name": "Korean"},
            {"code": "zh-CN", "name": "Chinese (Simplified)"},
            {"code": "zh-TW", "name": "Chinese (Traditional)"}
        ]
    
    def estimate_speech_duration(self, text: str) -> float:
        """Estimate speech duration in seconds based on text length"""
        # Estimate based on average speaking rate of 150 words per minute
        words = len(text.split())
        words_per_minute = 150
        duration_minutes = words / words_per_minute
        return duration_minutes * 60  # Convert to seconds
    
    def create_enhanced_tts(self, text: str, style: str = "friendly") -> bytes:
        """Create enhanced TTS with different speaking styles"""
        try:
            import requests
            
            # Adjust voice parameters based on style
            voice_configs = {
                "friendly": {
                    "name": "en-US-Neural2-F",
                    "speaking_rate": 0.95,
                    "pitch": 0.5,
                    "volume": 0.0
                },
                "professional": {
                    "name": "en-US-Neural2-C", 
                    "speaking_rate": 0.9,
                    "pitch": 0.0,
                    "volume": 0.0
                },
                "encouraging": {
                    "name": "en-US-Neural2-H",
                    "speaking_rate": 0.92,
                    "pitch": 1.0,
                    "volume": 2.0
                }
            }
            
            config = voice_configs.get(style, voice_configs["friendly"])
            
            payload = {
                "input": {"text": text},
                "voice": {
                    "languageCode": "en-US",
                    "name": config["name"],
                    "ssmlGender": "FEMALE"
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": config["speaking_rate"],
                    "pitch": config["pitch"],
                    "volumeGainDb": config["volume"],
                    "sampleRateHertz": 24000,
                    "effectsProfileId": ["telephony-class-application"]
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key
            }
            
            response = requests.post(
                f"{self.tts_api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                audio_content = result.get("audioContent", "")
                if audio_content:
                    return base64.b64decode(audio_content)
            
            return b''
                
        except Exception as e:
            logging.error(f"Enhanced TTS error: {e}")
            return b''
    
    def _detect_audio_format(self, audio_data: bytes) -> str:
        """Detect audio format from file header"""
        try:
            if len(audio_data) < 12:
                return "unknown"
            
            if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:20]:
                return "wav"
            elif audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
                return "mp3"
            elif audio_data.startswith(b'OggS'):
                return "ogg"
            elif audio_data.startswith(b'\x1a\x45\xdf\xa3'):
                return "webm"
            else:
                return "unknown"
                
        except Exception as e:
            logging.error(f"Format detection error: {e}")
            return "unknown"
    
    def _get_encoding_config(self, audio_format: str) -> Optional[dict]:
        """Get encoding configuration for Google Speech API based on audio format"""
        format_configs = {
            "wav": {
                "encoding": "LINEAR16",
                "sample_rate": 16000
            },
            "mp3": {
                "encoding": "MP3",
                "sample_rate": 16000
            },
            "ogg": {
                "encoding": "OGG_OPUS",
                "sample_rate": 16000
            },
            "webm": {
                "encoding": "WEBM_OPUS", 
                "sample_rate": 48000
            }
        }
        
        return format_configs.get(audio_format)
