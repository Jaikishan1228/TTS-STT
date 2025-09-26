from http.server import BaseHTTPRequestHandler
import json
import asyncio
import base64

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
            
            # Limit text length for serverless environment
            text = text[:1000]
            
            # Generate audio using edge-tts Python module directly
            try:
                import edge_tts
                
                async def generate_audio():
                    communicate = edge_tts.Communicate(text, voice)
                    audio_data = b""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data += chunk["data"]
                    return audio_data
                
                # Run the async function
                audio_data = asyncio.run(generate_audio())
                
                if audio_data:
                    # Encode audio as base64
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    response = {
                        "success": True,
                        "audio_data": audio_base64,
                        "message": f"Audio generated successfully ({len(audio_data)} bytes)"
                    }
                else:
                    response = {
                        "success": False, 
                        "error": "Failed to generate audio data"
                    }
                    
            except ImportError:
                response = {
                    "success": False,
                    "error": "edge-tts module not available"
                }
            except Exception as tts_error:
                response = {
                    "success": False,
                    "error": f"TTS generation error: {str(tts_error)}"
                }
            
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError:
            response = {"success": False, "error": "Invalid JSON format"}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            response = {"success": False, "error": f"Server error: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()