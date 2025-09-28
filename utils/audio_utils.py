import os
import io
import base64
import logging
from typing import Optional, Tuple
import tempfile

class AudioUtils:
    """Utility functions for audio processing"""
    
    def __init__(self):
        self.supported_formats = ['wav', 'mp3', 'ogg', 'webm']
        self.max_duration_seconds = 300  # 5 minutes max
        self.sample_rate = 16000  # Standard for speech recognition
    
    def validate_audio_file(self, audio_data: bytes) -> bool:
        """Validate if audio data is in a supported format"""
        try:
            # Check file size (basic validation)
            if len(audio_data) == 0:
                return False
            
            if len(audio_data) > 10 * 1024 * 1024:  # 10MB max
                return False
            
            # Basic header checks for common formats
            if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:20]:
                return True  # WAV file
            elif audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
                return True  # MP3 file
            elif audio_data.startswith(b'OggS'):
                return True  # OGG file
            elif audio_data.startswith(b'\x1a\x45\xdf\xa3'):
                return True  # WebM file
            
            # For other formats, assume valid if not empty and reasonable size
            return True
            
        except Exception as e:
            logging.error(f"Audio validation error: {e}")
            return False
    
    def convert_to_base64(self, audio_data: bytes) -> str:
        """Convert audio bytes to base64 string"""
        try:
            return base64.b64encode(audio_data).decode('utf-8')
        except Exception as e:
            logging.error(f"Base64 conversion error: {e}")
            return ""
    
    def convert_from_base64(self, base64_string: str) -> bytes:
        """Convert base64 string back to audio bytes"""
        try:
            return base64.b64decode(base64_string)
        except Exception as e:
            logging.error(f"Base64 decoding error: {e}")
            return b""
    
    def estimate_duration(self, audio_data: bytes, sample_rate: int = 16000) -> float:
        """Estimate audio duration in seconds (basic calculation)"""
        try:
            # This is a rough estimation for uncompressed audio
            if len(audio_data) < 44:  # Minimum for WAV header
                return 0.0
            
            # For WAV files, try to get actual duration from header
            if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:20]:
                try:
                    # Simple WAV duration calculation
                    data_size = len(audio_data) - 44  # Subtract header size
                    bytes_per_sample = 2  # Assuming 16-bit
                    channels = 2  # Assuming stereo
                    duration = data_size / (sample_rate * bytes_per_sample * channels)
                    return max(0.0, duration)
                except:
                    pass
            
            # Rough estimation for other formats
            # Assume compression ratio of about 10:1 for MP3
            estimated_uncompressed_size = len(audio_data) * 10
            duration = estimated_uncompressed_size / (sample_rate * 2 * 2)  # 16-bit stereo
            return max(0.0, min(duration, 300))  # Cap at 5 minutes
            
        except Exception as e:
            logging.error(f"Duration estimation error: {e}")
            return 0.0
    
    def save_audio_to_temp(self, audio_data: bytes, format: str = "wav") -> Optional[str]:
        """Save audio data to temporary file"""
        try:
            suffix = f".{format.lower()}"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(audio_data)
                return temp_file.name
        except Exception as e:
            logging.error(f"Error saving audio to temp file: {e}")
            return None
    
    def cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary audio file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logging.error(f"Error cleaning up temp file: {e}")
    
    def create_audio_player_html(self, audio_data: bytes, autoplay: bool = False) -> str:
        """Create HTML audio player with embedded audio data"""
        try:
            base64_audio = self.convert_to_base64(audio_data)
            autoplay_attr = "autoplay" if autoplay else ""
            
            html = f"""
            <div class="audio-player" style="margin: 10px 0;">
                <audio controls {autoplay_attr} style="width: 100%; max-width: 400px;">
                    <source src="data:audio/mpeg;base64,{base64_audio}" type="audio/mpeg">
                    <source src="data:audio/wav;base64,{base64_audio}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
            </div>
            """
            return html
        except Exception as e:
            logging.error(f"Error creating audio player HTML: {e}")
            return "<p style='color: #ff6b6b;'>Error loading audio player</p>"
    
    def get_audio_info(self, audio_data: bytes) -> dict:
        """Get basic information about audio data"""
        try:
            info = {
                "size_bytes": len(audio_data),
                "size_kb": round(len(audio_data) / 1024, 2),
                "size_mb": round(len(audio_data) / (1024 * 1024), 2),
                "estimated_duration": self.estimate_duration(audio_data),
                "format": self._detect_format(audio_data),
                "is_valid": self.validate_audio_file(audio_data),
                "sample_rate_estimated": self.sample_rate
            }
            return info
        except Exception as e:
            logging.error(f"Error getting audio info: {e}")
            return {
                "size_bytes": 0,
                "size_kb": 0,
                "size_mb": 0,
                "estimated_duration": 0,
                "format": "unknown",
                "is_valid": False,
                "sample_rate_estimated": 0
            }
    
    def _detect_format(self, audio_data: bytes) -> str:
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
            elif audio_data.startswith(b'ftyp'):
                return "m4a"
            else:
                return "unknown"
                
        except Exception as e:
            logging.error(f"Format detection error: {e}")
            return "unknown"
    
    def process_microphone_audio(self, audio_data: bytes) -> Tuple[bool, Optional[bytes], str]:
        """Process audio from microphone input"""
        try:
            # Validate the audio
            if not self.validate_audio_file(audio_data):
                return False, None, "Invalid audio format or corrupted data"
            
            # Check duration
            duration = self.estimate_duration(audio_data)
            if duration > self.max_duration_seconds:
                return False, None, f"Audio too long. Maximum duration is {self.max_duration_seconds} seconds"
            
            if duration < 0.5:  # Less than half second
                return False, None, "Audio too short. Please record for at least 1 second"
            
            # Audio is valid
            return True, audio_data, "Audio processed successfully"
            
        except Exception as e:
            logging.error(f"Audio processing error: {e}")
            return False, None, f"Error processing audio: {str(e)}"
    
    def create_silence(self, duration_seconds: float, sample_rate: int = 16000) -> bytes:
        """Create silent audio data for specified duration"""
        try:
            # Calculate number of samples
            num_samples = int(duration_seconds * sample_rate)
            
            # Create WAV header for 16-bit mono audio
            wav_header = bytearray()
            wav_header.extend(b'RIFF')
            wav_header.extend((36 + num_samples * 2).to_bytes(4, 'little'))
            wav_header.extend(b'WAVE')
            wav_header.extend(b'fmt ')
            wav_header.extend((16).to_bytes(4, 'little'))
            wav_header.extend((1).to_bytes(2, 'little'))  # PCM format
            wav_header.extend((1).to_bytes(2, 'little'))  # Mono
            wav_header.extend(sample_rate.to_bytes(4, 'little'))
            wav_header.extend((sample_rate * 2).to_bytes(4, 'little'))
            wav_header.extend((2).to_bytes(2, 'little'))
            wav_header.extend((16).to_bytes(2, 'little'))
            wav_header.extend(b'data')
            wav_header.extend((num_samples * 2).to_bytes(4, 'little'))
            
            # Add silent audio data (zeros)
            silence_data = bytes(num_samples * 2)  # 16-bit = 2 bytes per sample
            
            return bytes(wav_header) + silence_data
            
        except Exception as e:
            logging.error(f"Error creating silence: {e}")
            return b""
    
    def normalize_audio_volume(self, audio_data: bytes, target_level: float = 0.7) -> bytes:
        """Normalize audio volume (basic implementation)"""
        try:
            # This is a placeholder for audio normalization
            # In a real implementation, you would use audio processing libraries
            # For now, just return the original audio
            return audio_data
        except Exception as e:
            logging.error(f"Audio normalization error: {e}")
            return audio_data
