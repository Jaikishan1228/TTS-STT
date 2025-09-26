"""
High-quality Text-to-Speech module using Microsoft Edge TTS.
Provides neural voice synthesis with multiple language support.
"""

import asyncio
import base64
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports with graceful fallbacks
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("pygame not available - audio playback disabled")

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.error("edge-tts not available - TTS functionality disabled")

class TextToSpeech:
    """Text-to-Speech converter using Microsoft Edge TTS voices."""
    
    # Enhanced voice catalog with detailed metadata
    VOICES: Dict[str, Dict[str, str]] = {
        # English (US)
        'en-US-JennyNeural': {'name': 'Jenny', 'gender': 'Female', 'language': 'English (US)', 'style': 'Friendly'},
        'en-US-GuyNeural': {'name': 'Guy', 'gender': 'Male', 'language': 'English (US)', 'style': 'Friendly'},
        'en-US-AriaNeural': {'name': 'Aria', 'gender': 'Female', 'language': 'English (US)', 'style': 'News'},
        'en-US-DavisNeural': {'name': 'Davis', 'gender': 'Male', 'language': 'English (US)', 'style': 'News'},
        'en-US-JaneNeural': {'name': 'Jane', 'gender': 'Female', 'language': 'English (US)', 'style': 'Clear'},
        'en-US-JasonNeural': {'name': 'Jason', 'gender': 'Male', 'language': 'English (US)', 'style': 'Energetic'},
        'en-US-SaraNeural': {'name': 'Sara', 'gender': 'Female', 'language': 'English (US)', 'style': 'Gentle'},
        'en-US-TonyNeural': {'name': 'Tony', 'gender': 'Male', 'language': 'English (US)', 'style': 'Professional'},
        
        # English (UK)
        'en-GB-SoniaNeural': {'name': 'Sonia', 'gender': 'Female', 'language': 'English (UK)', 'style': 'British'},
        'en-GB-RyanNeural': {'name': 'Ryan', 'gender': 'Male', 'language': 'English (UK)', 'style': 'British'},
        
        # English (India)
        'en-IN-NeerjaNeural': {'name': 'Neerja', 'gender': 'Female', 'language': 'English (India)', 'style': 'Indian'},
        'en-IN-PrabhatNeural': {'name': 'Prabhat', 'gender': 'Male', 'language': 'English (India)', 'style': 'Indian'},
        
        # Spanish
        'es-ES-ElviraNeural': {'name': 'Elvira', 'gender': 'Female', 'language': 'Spanish (Spain)', 'style': 'Spanish'},
        'es-ES-AlvaroNeural': {'name': 'Alvaro', 'gender': 'Male', 'language': 'Spanish (Spain)', 'style': 'Spanish'},
        
        # French
        'fr-FR-DeniseNeural': {'name': 'Denise', 'gender': 'Female', 'language': 'French (France)', 'style': 'French'},
        'fr-FR-HenriNeural': {'name': 'Henri', 'gender': 'Male', 'language': 'French (France)', 'style': 'French'},
        
        # German
        'de-DE-KatjaNeural': {'name': 'Katja', 'gender': 'Female', 'language': 'German (Germany)', 'style': 'German'},
        'de-DE-ConradNeural': {'name': 'Conrad', 'gender': 'Male', 'language': 'German (Germany)', 'style': 'German'}
    }
    
    DEFAULT_VOICE = 'en-US-JennyNeural'
    
    def __init__(self, voice: str = None):
        """
        Initialize TTS with specified voice.
        
        Args:
            voice (str, optional): Voice ID from VOICES dictionary. Defaults to DEFAULT_VOICE.
        
        Raises:
            RuntimeError: If edge-tts is not available
        """
        if not EDGE_TTS_AVAILABLE:
            raise RuntimeError("edge-tts package is required. Install with: pip install edge-tts")
        
        self.voice = voice if voice and voice in self.VOICES else self.DEFAULT_VOICE
        self._audio_initialized = False
        
        # Initialize pygame if available
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self._audio_initialized = True
                logger.info("Audio playback initialized")
            except pygame.error as e:
                logger.warning(f"Audio initialization failed: {e}")
        
        voice_info = self.VOICES.get(self.voice, {'name': 'Unknown', 'language': 'Unknown'})
        logger.info(f"TTS initialized with voice: {voice_info['name']} ({voice_info['language']})")
    
    @classmethod
    def list_voices(cls) -> None:
        """Display all available voices in a formatted table."""
        print("🎭 Available Neural Voices:")
        print("-" * 80)
        print(f"{'Voice ID':<25} {'Name':<12} {'Language':<18} {'Gender':<8} {'Style':<12}")
        print("-" * 80)
        
        for voice_id, info in cls.VOICES.items():
            print(f"{voice_id:<25} {info['name']:<12} {info['language']:<18} "
                  f"{info['gender']:<8} {info['style']:<12}")
        
        print("-" * 80)
        print(f"Total voices available: {len(cls.VOICES)}")
    
    @classmethod
    def get_voices_by_language(cls, language_code: str) -> Dict[str, Dict[str, str]]:
        """
        Get voices filtered by language code.
        
        Args:
            language_code (str): Language code like 'en-US', 'en-GB', etc.
            
        Returns:
            Dict: Filtered voices dictionary
        """
        return {k: v for k, v in cls.VOICES.items() if k.startswith(language_code)}
    
    def set_voice(self, voice: str) -> bool:
        """
        Change the current voice.
        
        Args:
            voice (str): New voice ID
            
        Returns:
            bool: True if voice was set successfully
        """
        if voice in self.VOICES:
            self.voice = voice
            print(f"✅ Voice changed to: {self.VOICES[voice]}")
            return True
        else:
            print(f"❌ Voice '{voice}' not found. Use list_voices() to see available options.")
            return False
    
    def speak(self, text: str, rate: str = "+0%", volume: str = "+0%") -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to convert to speech
            rate (str): Speech rate (e.g., "+20%", "-10%")
            volume (str): Volume level (e.g., "+10%", "-5%")
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not text.strip():
            print("❌ No text provided")
            return False
        
        # Split long text into chunks
        chunks = textwrap.wrap(text, 1000)
        
        for i, chunk in enumerate(chunks):
            if not self._speak_chunk(chunk, rate, volume):
                return False
        
        return True
    
    def _speak_chunk(self, text: str, rate: str, volume: str) -> bool:
        """Speak a single chunk of text."""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            audio_file = temp_file.name
        
        try:
            # Build edge-tts command
            command = [
                "edge-tts",
                "--voice", self.voice,
                "--text", text,
                "--rate", rate,
                "--volume", volume,
                "--write-media", audio_file
            ]
            
            # Execute TTS command
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ TTS Error: {result.stderr}")
                return False
            
            if not os.path.exists(audio_file):
                print("❌ Audio file not generated")
                return False
            
            # Play audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        finally:
            # Clean up temp file
            if os.path.exists(audio_file):
                try:
                    pygame.mixer.music.unload()
                    os.unload(audio_file)
                except:
                    pass
    
    def save_audio(self, text: str, filename: str, rate: str = "+0%", volume: str = "+0%") -> bool:
        """
        Save text as audio file without playing.
        
        Args:
            text (str): Text to convert
            filename (str): Output filename (should end with .mp3 or .wav)
            rate (str): Speech rate (e.g., "+20%", "-10%")
            volume (str): Volume level (e.g., "+10%", "-5%")
            
        Returns:
            bool: True if successful
        """
        try:
            # Use basic command without rate/volume for now to avoid parameter issues
            command = [
                "edge-tts",
                "--voice", self.voice,
                "--text", text,
                "--write-media", filename
            ]
            
            print(f"🎤 Running command: edge-tts --voice {self.voice} --text '{text[:30]}...' --write-media {filename}")
            
            result = subprocess.run(command, capture_output=True, text=True, shell=False)
            
            if result.returncode == 0:
                print(f"✅ Audio saved to: {filename}")
                return True
            else:
                print(f"❌ Failed to save audio: {result.stderr}")
                print(f"❌ Return code: {result.returncode}")
                if result.stdout:
                    print(f"❌ Stdout: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return False

def main():
    """Demo function showing TTS usage."""
    tts = TextToSpeech()
    
    print("🗣️  Text-to-Speech Demo")
    print("\nAvailable commands:")
    print("1. Type text to speak")
    print("2. 'voices' - List all voices")  
    print("3. 'voice <voice_id>' - Change voice")
    print("4. 'quit' - Exit")
    
    while True:
        user_input = input("\n💬 Enter text or command: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'voices':
            TextToSpeech.list_voices()
        elif user_input.lower().startswith('voice '):
            voice_id = user_input[6:].strip()
            tts.set_voice(voice_id)
        elif user_input:
            print(f"🔊 Speaking: {user_input[:50]}{'...' if len(user_input) > 50 else ''}")
            tts.speak(user_input)
        else:
            print("❌ Please enter some text")

if __name__ == "__main__":
    main()
