"""
Advanced Speech-to-Text module with multiple backend support.
Supports both web-based and Python-native speech recognition.
"""

import logging
import time
import threading
from typing import Optional, Callable, Dict, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Web-based STT imports with graceful fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import WebDriverException, TimeoutException
    WEB_STT_AVAILABLE = True
    logger.info("Web STT backend available")
except ImportError as e:
    WEB_STT_AVAILABLE = False
    logger.warning(f"Web STT not available: {e}")

# Python-native STT imports with graceful fallback
try:
    import speech_recognition as sr
    import pyaudio
    PYTHON_STT_AVAILABLE = True
    logger.info("Python STT backend available")
except ImportError as e:
    PYTHON_STT_AVAILABLE = False
    logger.warning(f"Python STT not available: {e}")

class WebSTT:
    """Web-based Speech-to-Text converter using online service."""

    def __init__(self, language: str = "en-US", headless: bool = True, use_local: bool = False):
        """
        Initialize the web-based STT.
        
        Args:
            language (str): Language code (e.g., 'en-US', 'en-IN', 'es-ES')
            headless (bool): Run browser in headless mode
            use_local (bool): Use local HTML file instead of Vercel service
        """
        if not WEB_STT_AVAILABLE:
            raise ImportError("Web STT requires selenium. Install with: pip install selenium")
        
        # Choose between local HTML file or online service
        if use_local:
            import os
            local_path = os.path.join(os.path.dirname(__file__), "index.html")
            if os.path.exists(local_path):
                self.website_path = f"file:///{local_path.replace(os.sep, '/')}"
                print("🏠 Using local STT+TTS interface")
            else:
                self.website_path = "https://stt-web-beta.vercel.app"
                print("⚠️ Local file not found, using online service")
        else:
            self.website_path = "https://stt-web-beta.vercel.app"
            print("🌐 Using online STT service")
        
        self.language = language
        
        # Configure Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--use-fake-ui-for-media-stream")
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--allow-running-insecure-content")
        if headless:
            self.chrome_options.add_argument("--headless=new")
        
        self.driver = webdriver.Chrome(service=Service(), options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        print(f"🌐 Web STT initialized with language: {language}")

    def _display_listening_status(self, content: str = ""):
        """Display real-time transcription."""
        if content:
            print(f"\r🎤 Listening: {content}", end='', flush=True)
        else:
            print("\r🎤 Listening...", end='', flush=True)

    def _get_transcribed_text(self) -> str:
        """Get the current transcribed text from the webpage."""
        return self.driver.find_element(By.ID, "convert_text").text

    def _set_language(self):
        """Set the recognition language."""
        self.driver.execute_script(f"""
            var select = document.getElementById('language_select');
            select.value = '{self.language}';
            select.dispatchEvent(new Event('change'));
        """)

    def listen(self, display_realtime: bool = True) -> Optional[str]:
        """
        Start listening and return transcribed speech.
        
        Args:
            display_realtime (bool): Show real-time transcription
            
        Returns:
            str: Transcribed text or None if error
        """
        try:
            # Load the website and set language
            self.driver.get(self.website_path)
            self.wait.until(EC.presence_of_element_located((By.ID, "language_select")))
            self._set_language()
            
            # Start recording
            self.driver.find_element(By.ID, "click_to_record").click()
            self.wait.until(EC.presence_of_element_located((By.ID, "is_recording")))
            
            if display_realtime:
                self._display_listening_status()
            
            # Monitor recording and capture text
            last_text = ""
            while True:
                current_text = self._get_transcribed_text()
                
                if display_realtime and current_text != last_text:
                    self._display_listening_status(current_text)
                    last_text = current_text
                
                # Check if recording is still active
                recording_status = self.driver.find_element(By.ID, "is_recording").text
                if not recording_status.startswith("Recording: True"):
                    break
                    
                time.sleep(0.1)
            
            final_text = self._get_transcribed_text()
            if display_realtime:
                print(f"\r✅ Transcription: {final_text}\n")
            
            return final_text if final_text else None
            
        except Exception as e:
            print(f"❌ Error during speech recognition: {e}")
            return None

    def close(self):
        """Close the browser driver."""
        if self.driver:
            self.driver.quit()

class PythonSTT:
    """Native Python Speech-to-Text using SpeechRecognition library."""
    
    def __init__(self, language: str = "en-US", energy_threshold: int = 300):
        """
        Initialize Python-based STT.
        
        Args:
            language (str): Language code (e.g., 'en-US', 'en-GB')
            energy_threshold (int): Microphone sensitivity (lower = more sensitive)
        """
        if not PYTHON_STT_AVAILABLE:
            raise ImportError("Python STT requires speech_recognition and pyaudio. Install with: pip install SpeechRecognition pyaudio")
        
        self.language = language
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Calibrate microphone
        print("🎤 Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print(f"✅ Python STT initialized (Language: {language})")
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10, display_realtime: bool = True) -> Optional[str]:
        """
        Listen for a single phrase and return transcription.
        
        Args:
            timeout (int): Seconds to wait for speech to start
            phrase_time_limit (int): Maximum seconds to listen for phrase
            display_realtime (bool): Show status messages
            
        Returns:
            str: Transcribed text or None if no speech
        """
        try:
            if display_realtime:
                print("🎙️ Listening...")
            
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            if display_realtime:
                print("🔄 Processing...")
            
            # Try Google Speech Recognition (free)
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                if display_realtime:
                    print(f"✅ Transcription: {text}")
                return text
            except sr.UnknownValueError:
                if display_realtime:
                    print("❌ Could not understand audio")
                return None
            except sr.RequestError as e:
                if display_realtime:
                    print(f"❌ Google API error: {e}")
                # Try offline recognition as fallback
                return self._try_offline_recognition(audio, display_realtime)
        
        except sr.WaitTimeoutError:
            if display_realtime:
                print("⏰ No speech detected within timeout period")
            return None
        except Exception as e:
            if display_realtime:
                print(f"❌ Error: {e}")
            return None
    
    def _try_offline_recognition(self, audio, display_realtime: bool = True) -> Optional[str]:
        """Try offline speech recognition as fallback."""
        try:
            text = self.recognizer.recognize_sphinx(audio)
            if display_realtime:
                print(f"✅ Offline transcription: {text}")
            return text
        except Exception:
            if display_realtime:
                print("❌ Offline recognition not available")
            return None
    
    def close(self):
        """Clean up resources (no cleanup needed for Python STT)."""
        pass

class SpeechToTextListener:
    """Unified Speech-to-Text interface with multiple backend options."""
    
    def __init__(self, method: str = "auto", language: str = "en-US", use_local: bool = False, **kwargs):
        """
        Initialize STT with specified method.
        
        Args:
            method (str): "auto", "web", "python", or "hybrid"
            language (str): Language code
            use_local (bool): Use local HTML interface for web STT
            **kwargs: Additional arguments for specific methods
        """
        self.method = method
        self.language = language
        self.use_local = use_local
        self.kwargs = kwargs
        self.active_stt = None
        
        if method == "auto":
            self.method = self._detect_best_method()
        
        self._initialize_stt()
    
    def _detect_best_method(self) -> str:
        """Automatically detect the best available STT method."""
        if PYTHON_STT_AVAILABLE:
            print("🔍 Auto-detected: Python STT (recommended)")
            return "python"
        elif WEB_STT_AVAILABLE:
            print("🔍 Auto-detected: Web STT")
            return "web"
        else:
            raise RuntimeError("No STT methods available. Install dependencies.")
    
    def _initialize_stt(self):
        """Initialize the selected STT method."""
        try:
            if self.method == "web":
                self.active_stt = WebSTT(language=self.language, use_local=self.use_local, **self.kwargs)
            elif self.method == "python":
                self.active_stt = PythonSTT(language=self.language, **self.kwargs)
            elif self.method == "hybrid":
                # Try Python first, fallback to Web
                try:
                    self.active_stt = PythonSTT(language=self.language, **self.kwargs)
                    self.method = "python"
                except ImportError:
                    self.active_stt = WebSTT(language=self.language, use_local=self.use_local, **self.kwargs)
                    self.method = "web"
            else:
                raise ValueError(f"Unknown STT method: {self.method}")
                
        except Exception as e:
            print(f"❌ Failed to initialize {self.method} STT: {e}")
            if self.method != "web" and WEB_STT_AVAILABLE:
                print("🔄 Falling back to Web STT...")
                self.active_stt = WebSTT(language=self.language, use_local=self.use_local, **self.kwargs)
                self.method = "web"
            else:
                raise
    
    def listen(self, display_realtime: bool = True, **kwargs) -> Optional[str]:
        """
        Listen for speech using the active STT method.
        
        Args:
            display_realtime (bool): Show real-time feedback
            **kwargs: Method-specific arguments
            
        Returns:
            str: Transcribed text or None if error
        """
        if not self.active_stt:
            print("❌ No active STT method")
            return None
        
        print(f"🎯 Using {self.method.upper()} STT...")
        return self.active_stt.listen(display_realtime=display_realtime, **kwargs)
    
    def switch_method(self, new_method: str, **kwargs):
        """
        Switch to a different STT method.
        
        Args:
            new_method (str): "web", "python", or "hybrid"
            **kwargs: New method arguments
        """
        if self.active_stt:
            self.active_stt.close()
        
        self.method = new_method
        self.kwargs = kwargs
        self._initialize_stt()
        print(f"✅ Switched to {new_method.upper()} STT")
    
    def close(self):
        """Close the active STT method."""
        if self.active_stt:
            self.active_stt.close()
    
    @staticmethod
    def list_methods():
        """List all available STT methods."""
        print("🎤 Available STT Methods:")
        print("-" * 40)
        
        if WEB_STT_AVAILABLE:
            print("✅ web     - Web-based STT (stt-web-beta.vercel.app)")
        else:
            print("❌ web     - Not available (install selenium)")
            
        if PYTHON_STT_AVAILABLE:
            print("✅ python  - Native Python STT (Google Speech API)")
        else:
            print("❌ python  - Not available (install speech_recognition, pyaudio)")
            
        print("🔄 auto    - Automatically choose best available")
        print("🎯 hybrid  - Try Python first, fallback to Web")

def main():
    """Interactive STT demo with method selection."""
    print("🎙️  Advanced Speech-to-Text System")
    print("=" * 50)
    
    # Show available methods
    SpeechToTextListener.list_methods()
    
    print("\n💡 Usage Examples:")
    print("- 'auto' or 'a' - Auto-detect best method")
    print("- 'web' or 'w' - Web-based STT (Vercel)")
    print("- 'local' or 'l' - Local STT+TTS interface")
    print("- 'python' or 'p' - Python native STT")
    print("- 'hybrid' or 'h' - Hybrid approach")
    print("- 'quit' or 'q' - Exit")
    
    while True:
        try:
            method_input = input("\n🎯 Choose STT method: ").strip().lower()
            
            if method_input in ['quit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Map short forms to full names
            method_map = {
                'a': 'auto', 'w': 'web', 'l': 'local', 'p': 'python', 'h': 'hybrid',
                'auto': 'auto', 'web': 'web', 'local': 'local', 'python': 'python', 'hybrid': 'hybrid'
            }
            
            if method_input not in method_map:
                print("❌ Invalid method. Please choose: auto, web, local, python, hybrid, or quit")
                continue
            
            method = method_map[method_input]
            use_local = (method == 'local')
            if use_local:
                method = 'web'  # Local is a variant of web method
            
            # Get language preference
            language = input("🌍 Language (default: en-US): ").strip() or "en-US"
            
            # Initialize STT
            method_display = "LOCAL STT+TTS" if use_local else method.upper()
            print(f"\n🚀 Initializing {method_display} STT...")
            stt = SpeechToTextListener(method=method, language=language, use_local=use_local)
            
            try:
                while True:
                    print(f"\n🎤 Ready to listen using {stt.method.upper()} STT")
                    print("Press Enter to start listening, 's' to switch method, or 'q' to quit")
                    
                    user_input = input("Action: ").strip().lower()
                    
                    if user_input == 'q':
                        break
                    elif user_input == 's':
                        stt.close()
                        break  # Go back to method selection
                    elif user_input == '':
                        # Start listening
                        print("\n🎙️ Listening... Speak now!")
                        
                        text = stt.listen(display_realtime=True)
                        
                        if text:
                            print(f"\n📝 Result: {text}")
                            
                            # Ask if user wants to continue
                            continue_input = input("\n🔄 Listen again? (y/n): ").strip().lower()
                            if continue_input not in ['y', 'yes', '']:
                                break
                        else:
                            print("❌ No speech detected or error occurred")
                    else:
                        print("❌ Invalid input. Press Enter to listen, 's' to switch, or 'q' to quit")
                        
            finally:
                stt.close()
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("🔄 Returning to method selection...")
            continue

def quick_demo(method: str = "auto", language: str = "en-US"):
    """Quick single-use demo function."""
    print(f"🎙️ Quick STT Demo - {method.upper()} method")
    
    stt = SpeechToTextListener(method=method, language=language)
    
    try:
        print("Speak into your microphone...")
        text = stt.listen(display_realtime=True)
        
        if text:
            print(f"📝 Result: {text}")
            return text
        else:
            print("❌ No speech detected")
            return None
            
    finally:
        stt.close()

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        method = sys.argv[1] if sys.argv[1] in ['web', 'python', 'hybrid', 'auto'] else 'auto'
        language = sys.argv[2] if len(sys.argv) > 2 else 'en-US'
        quick_demo(method, language)
    else:
        main()
