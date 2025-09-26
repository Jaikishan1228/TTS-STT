import textwrap
import os
import pygame
import subprocess
import tempfile
from typing import Optional, List

class TextToSpeech:
    """Text-to-Speech converter using Microsoft Edge TTS voices."""
    
    # Available voice options
    VOICES = {
        'en-US-JennyNeural': 'English (US) - Jenny (Female)',
        'en-US-GuyNeural': 'English (US) - Guy (Male)', 
        'en-US-AriaNeural': 'English (US) - Aria (Female)',
        'en-US-DavisNeural': 'English (US) - Davis (Male)',
        'en-US-JaneNeural': 'English (US) - Jane (Female)',
        'en-US-JasonNeural': 'English (US) - Jason (Male)',
        'en-US-SaraNeural': 'English (US) - Sara (Female)',
        'en-US-TonyNeural': 'English (US) - Tony (Male)',
        'en-GB-SoniaNeural': 'English (UK) - Sonia (Female)',
        'en-GB-RyanNeural': 'English (UK) - Ryan (Male)',
        'en-IN-NeerjaNeural': 'English (India) - Neerja (Female)',
        'en-IN-PrabhatNeural': 'English (India) - Prabhat (Male)',
        'es-ES-ElviraNeural': 'Spanish (Spain) - Elvira (Female)',
        'es-ES-AlvaroNeural': 'Spanish (Spain) - Alvaro (Male)',
        'fr-FR-DeniseNeural': 'French (France) - Denise (Female)',
        'fr-FR-HenriNeural': 'French (France) - Henri (Male)',
        'de-DE-KatjaNeural': 'German (Germany) - Katja (Female)',
        'de-DE-ConradNeural': 'German (Germany) - Conrad (Male)'
    }
    
    def __init__(self, voice: str = 'en-US-JennyNeural'):
        """
        Initialize TTS with specified voice.
        
        Args:
            voice (str): Voice ID from VOICES dictionary
        """
        self.voice = voice if voice in self.VOICES else 'en-US-JennyNeural'
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print(f"🔊 TTS initialized with voice: {self.VOICES.get(self.voice, self.voice)}")
    
    @classmethod
    def list_voices(cls) -> None:
        """Display all available voices."""
        print("🎭 Available Voices:")
        print("-" * 50)
        for voice_id, description in cls.VOICES.items():
            print(f"{voice_id:<25} - {description}")
    
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
