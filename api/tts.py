from http.server import BaseHTTPRequestHandler
import json
import os
import tempfile
import subprocess
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Handle CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            voice = data.get('voice', 'en-US-JennyNeural')
            
            if not text:
                response = {"success": False, "error": "No text provided"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate audio using edge-tts with timeout
            cmd = [
                'edge-tts',
                '--voice', voice,
                '--text', text[:1000],  # Limit text length for serverless
                '--write-media', temp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                # Read audio file and encode as base64
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                import base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Clean up temp file
                os.unlink(temp_path)
                
                response = {
                    "success": True,
                    "audio_data": audio_base64,
                    "message": "Audio generated successfully"
                }
            else:
                response = {
                    "success": False, 
                    "error": f"TTS generation failed: {result.stderr}"
                }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()