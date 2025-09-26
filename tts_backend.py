#!/usr/bin/env python3
"""
TTS Backend Server - Speech Processing Suite
Provides HTTP API endpoints for Text-to-Speech functionality.

Features:
- Neural TTS voices via Microsoft Edge TTS
- Automatic file cleanup and management
- CORS support for web interface
- Both local development and production deployment support

Usage:
    python tts_backend.py
    
Then open: http://localhost:8000
"""

import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser

# Import our TTS module
try:
    from TTS import TextToSpeech
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ TTS.py module not available")

class TTSHandler(BaseHTTPRequestHandler):
    """HTTP handler for TTS requests"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve the main HTML file
            self.serve_html_file()
        elif parsed_path.path == '/voices':
            # Return available voices list
            self.send_voices_list()
        elif parsed_path.path == '/test':
            # Test endpoint
            self.send_test_response()
        elif parsed_path.path.startswith('/audio/'):
            # Serve generated audio files
            self.serve_audio_file(parsed_path.path)
        elif parsed_path.path == '/cleanup':
            # Clean up temporary files
            self.handle_cleanup_request()
        else:
            self.send_error(404, "Not Found")
    
    def send_test_response(self):
        """Send a test response to verify the server is working"""
        test_data = {
            "status": "Server is running",
            "tts_available": TTS_AVAILABLE,
            "timestamp": str(time.time()),
            "endpoints": ["/", "/voices", "/tts", "/audio/", "/test"]
        }
        
        if TTS_AVAILABLE:
            try:
                from TTS import TextToSpeech
                tts = TextToSpeech()
                test_data["current_voice"] = tts.voice
                test_data["tts_ready"] = True
            except Exception as e:
                test_data["tts_error"] = str(e)
                test_data["tts_ready"] = False
        
        self.send_json_response(test_data)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/tts':
            self.handle_tts_request()
        elif parsed_path.path == '/cleanup':
            self.handle_cleanup_request()
        else:
            self.send_error(404, "Not Found")
    
    def serve_html_file(self):
        """Serve the main HTML interface"""
        try:
            # Try multiple possible HTML file locations
            possible_files = [
                "index.html",
                "stt_tts_unified.html", 
                os.path.join(os.path.dirname(__file__), "index.html"),
                os.path.join(os.path.dirname(__file__), "stt_tts_unified.html")
            ]
            
            html_content = None
            used_file = None
            
            for html_path in possible_files:
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                        used_file = html_path
                        break
                except FileNotFoundError:
                    continue
            
            if html_content is None:
                self.send_error(404, "HTML file not found. Please ensure stt_tts_unified.html exists.")
                return
            
            print(f"📄 Serving HTML file: {used_file}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Error serving HTML: {str(e)}")
            self.send_error(500, f"Server error: {str(e)}")
    
    def send_voices_list(self):
        """Send list of available TTS voices"""
        if not TTS_AVAILABLE:
            voices = {"error": "TTS not available"}
        else:
            # Get voices from TTS module
            tts = TextToSpeech()
            voices = {
                "voices": [
                    {"id": "en-US-JennyNeural", "name": "Jenny (US) - Friendly Female", "lang": "en-US"},
                    {"id": "en-US-GuyNeural", "name": "Guy (US) - Friendly Male", "lang": "en-US"},
                    {"id": "en-US-AriaNeural", "name": "Aria (US) - News Female", "lang": "en-US"},
                    {"id": "en-US-DavisNeural", "name": "Davis (US) - News Male", "lang": "en-US"},
                    {"id": "en-US-AmberNeural", "name": "Amber (US) - Warm Female", "lang": "en-US"},
                    {"id": "en-US-AnaNeural", "name": "Ana (US) - Child Female", "lang": "en-US"},
                    {"id": "en-US-BrandonNeurai", "name": "Brandon (US) - Young Male", "lang": "en-US"},
                    {"id": "en-US-ChristopherNeural", "name": "Christopher (US) - Professional Male", "lang": "en-US"},
                    {"id": "en-US-CoraNeural", "name": "Cora (US) - Mature Female", "lang": "en-US"},
                    {"id": "en-US-ElizabethNeural", "name": "Elizabeth (US) - Calm Female", "lang": "en-US"},
                    {"id": "en-US-EricNeural", "name": "Eric (US) - Casual Male", "lang": "en-US"},
                    {"id": "en-US-JacobNeural", "name": "Jacob (US) - Conversational Male", "lang": "en-US"},
                    {"id": "en-US-JaneNeural", "name": "Jane (US) - Clear Female", "lang": "en-US"},
                    {"id": "en-US-JasonNeural", "name": "Jason (US) - Energetic Male", "lang": "en-US"},
                    {"id": "en-US-MichelleNeural", "name": "Michelle (US) - Expressive Female", "lang": "en-US"},
                    {"id": "en-US-MonicaNeural", "name": "Monica (US) - Pleasant Female", "lang": "en-US"},
                    {"id": "en-US-NancyNeural", "name": "Nancy (US) - Storyteller Female", "lang": "en-US"},
                    {"id": "en-US-RogerNeural", "name": "Roger (US) - Deep Male", "lang": "en-US"},
                    {"id": "en-US-SaraNeural", "name": "Sara (US) - Gentle Female", "lang": "en-US"},
                    {"id": "en-US-SteffanNeural", "name": "Steffan (US) - Warm Male", "lang": "en-US"},
                    {"id": "en-GB-SoniaNeural", "name": "Sonia (UK) - British Female", "lang": "en-GB"},
                    {"id": "en-GB-RyanNeural", "name": "Ryan (UK) - British Male", "lang": "en-GB"},
                    {"id": "en-AU-NatashaNeural", "name": "Natasha (AU) - Australian Female", "lang": "en-AU"},
                    {"id": "en-AU-WilliamNeural", "name": "William (AU) - Australian Male", "lang": "en-AU"},
                    {"id": "en-CA-ClaraNeural", "name": "Clara (CA) - Canadian Female", "lang": "en-CA"},
                    {"id": "en-CA-LiamNeural", "name": "Liam (CA) - Canadian Male", "lang": "en-CA"},
                    {"id": "en-IN-NeerjaNeural", "name": "Neerja (IN) - Indian Female", "lang": "en-IN"},
                    {"id": "en-IN-PrabhatNeural", "name": "Prabhat (IN) - Indian Male", "lang": "en-IN"}
                ]
            }
        
        self.send_json_response(voices)
    
    def handle_tts_request(self):
        """Handle TTS generation requests"""
        print("🔊 Received TTS request")
        
        if not TTS_AVAILABLE:
            error_msg = "TTS module not available. Please install edge-tts and pygame."
            print(f"❌ {error_msg}")
            self.send_json_response({"success": False, "error": error_msg}, 500)
            return
        
        try:
            # Read POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            if not post_data:
                self.send_json_response({"success": False, "error": "No data received"}, 400)
                return
                
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            voice = data.get('voice', 'en-US-JennyNeural')
            rate = data.get('rate', 1.0)
            volume = data.get('volume', 0.8)
            
            print(f"📝 TTS Request - Text: '{text[:50]}...', Voice: {voice}, Rate: {rate}, Volume: {volume}")
            
            if not text:
                self.send_json_response({"success": False, "error": "No text provided"}, 400)
                return
            
            if len(text) > 5000:  # Reasonable limit
                self.send_json_response({"success": False, "error": "Text too long (max 5000 characters)"}, 400)
                return
            
            # Clean up old temporary files first (files older than 1 hour)
            self.cleanup_old_files()
            
            # Create TTS instance and generate audio
            print(f"🎤 Creating TTS instance with voice: {voice}")
            tts = TextToSpeech(voice=voice)
            
            # Generate unique filename
            import time
            filename = f"tts_temp_{int(time.time())}.mp3"
            filepath = os.path.join("audio", filename)
            
            # Create audio directory if it doesn't exist
            os.makedirs("audio", exist_ok=True)
            
            # Convert rate and volume to edge-tts format
            # Rate: 1.0 = +0%, 1.5 = +50%, 0.5 = -50%
            rate_percent = int((rate - 1) * 100)
            rate_str = f"{rate_percent:+d}%" if rate_percent != 0 else "+0%"
            
            # Volume: 1.0 = +0%, 0.8 = -20%, 1.2 = +20%  
            volume_percent = int((volume - 1) * 100)
            volume_str = f"{volume_percent:+d}%" if volume_percent != 0 else "+0%"
            
            print(f"🔧 Rate conversion: {rate} -> {rate_str}, Volume: {volume} -> {volume_str}")
            
            # Apply custom rate and volume settings if supported
            try:
                # For now, let's use basic generation without custom rate/volume to avoid edge-tts issues
                print(f"🎵 Generating audio with basic parameters...")
                success = tts.save_audio(text, filepath)
                
                if success and os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    response = {
                        "success": True,
                        "audio_url": f"/audio/{filename}",
                        "filename": filename,
                        "text": text,
                        "voice": voice,
                        "rate": rate,
                        "volume": volume,
                        "file_size": file_size,
                        "message": f"Audio generated successfully ({file_size} bytes)",
                        "cleanup_info": "File will be auto-deleted after download or on page refresh"
                    }
                    print(f"✅ Generated audio: {filename} ({file_size} bytes) with voice {voice}")
                else:
                    response = {"success": False, "error": "Failed to generate audio file"}
                    print(f"❌ Audio generation failed for voice: {voice}")
            except Exception as audio_error:
                response = {"success": False, "error": f"Audio generation error: {str(audio_error)}"}
                print(f"❌ TTS Error: {audio_error}")
                
            self.send_json_response(response)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            print(f"❌ JSON Error: {error_msg}")
            self.send_json_response({"success": False, "error": error_msg}, 400)
        except Exception as e:
            error_msg = f"Server error: {str(e)}"
            print(f"❌ Server Error: {error_msg}")
            self.send_json_response({"success": False, "error": error_msg}, 500)
    
    def cleanup_old_files(self):
        """Clean up temporary audio files older than 1 hour"""
        try:
            audio_dir = "audio"
            if not os.path.exists(audio_dir):
                return
                
            current_time = time.time()
            max_age = 3600  # 1 hour in seconds
            cleaned_count = 0
            
            for filename in os.listdir(audio_dir):
                if filename.startswith("tts_temp_"):
                    filepath = os.path.join(audio_dir, filename)
                    try:
                        file_age = current_time - os.path.getctime(filepath)
                        if file_age > max_age:
                            os.remove(filepath)
                            cleaned_count += 1
                            print(f"🗑️ Cleaned up old temp file: {filename}")
                    except Exception as e:
                        print(f"⚠️ Failed to clean up {filename}: {e}")
                        
            if cleaned_count > 0:
                print(f"🧹 Cleaned up {cleaned_count} old temporary files")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    def handle_cleanup_request(self):
        """Handle manual cleanup requests (e.g., on page refresh)"""
        try:
            cleaned_count = 0
            audio_dir = "audio"
            
            if os.path.exists(audio_dir):
                for filename in os.listdir(audio_dir):
                    if filename.startswith("tts_temp_"):
                        filepath = os.path.join(audio_dir, filename)
                        try:
                            os.remove(filepath)
                            cleaned_count += 1
                        except Exception as e:
                            print(f"⚠️ Failed to clean up {filename}: {e}")
            
            response = {
                "success": True,
                "cleaned_files": cleaned_count,
                "message": f"Cleaned up {cleaned_count} temporary files"
            }
            print(f"🧹 Manual cleanup: removed {cleaned_count} temp files")
            self.send_json_response(response)
            
        except Exception as e:
            error_msg = f"Cleanup error: {str(e)}"
            print(f"❌ {error_msg}")
            self.send_json_response({"success": False, "error": error_msg}, 500)
    
    def serve_audio_file(self, path):
        """Serve generated audio files and schedule cleanup"""
        try:
            filename = os.path.basename(path)
            filepath = os.path.join("audio", filename)
            
            if not os.path.exists(filepath):
                self.send_error(404, "Audio file not found")
                return
            
            with open(filepath, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(content)
            
            # Schedule cleanup of temporary files after serving
            if filename.startswith("tts_temp_"):
                def delayed_cleanup():
                    import time
                    time.sleep(30)  # Wait 30 seconds after serving to allow multiple downloads
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            print(f"🗑️ Auto-cleaned temp file: {filename}")
                    except Exception as e:
                        print(f"⚠️ Failed to auto-clean {filename}: {e}")
                
                threading.Thread(target=delayed_cleanup, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Error serving audio file: {e}")
            self.send_error(500, f"Server error: {str(e)}")
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response with CORS headers"""
        json_data = json.dumps(data, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"🌐 {self.address_string()} - {format % args}")

def run_server(port=8000):
    """Run the TTS backend server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TTSHandler)
    
    print(f"🚀 TTS Backend Server starting on port {port}")
    print(f"📱 Access your STT+TTS interface at: http://localhost:{port}")
    print(f"🔧 TTS Module Available: {'✅ Yes' if TTS_AVAILABLE else '❌ No'}")
    print("🔄 Press Ctrl+C to stop the server\n")
    
    # Optionally open browser
    try:
        webbrowser.open(f'http://localhost:{port}')
        print("🌐 Opened browser automatically")
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⚠️ Server stopped by user")
        httpd.shutdown()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TTS Backend Server')
    parser.add_argument('--port', type=int, default=8000, 
                       help='Port to run the server on (default: 8000)')
    parser.add_argument('--no-browser', action='store_true',
                       help='Don\'t open browser automatically')
    
    args = parser.parse_args()
    
    print("🎙️ STT & TTS Backend Server")
    print("=" * 50)
    
    if not TTS_AVAILABLE:
        print("⚠️ Warning: TTS.py module not available")
        print("   TTS functionality will be limited to Web Speech API")
        print("   Install edge-tts and pygame for full TTS support")
        print()
    
    run_server(args.port)

if __name__ == '__main__':
    main()