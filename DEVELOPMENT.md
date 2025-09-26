# Development Guide

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements-local.txt

# Start server
python tts_backend.py

# Access app
http://localhost:8000
```

### Production Deployment
- Vercel deployment uses `requirements.txt` (minimal dependencies)
- Live demo: https://tts-stt-ivory.vercel.app

## Architecture

### Frontend (index.html)
- Pure HTML/CSS/JS
- Web Speech API for STT
- SpeechSynthesis API for TTS
- Enhanced browser compatibility

### Backend (tts_backend.py)
- Python HTTP server
- Static file serving
- TTS API endpoints
- Audio file management

### TTS Module (TTS.py)
- Microsoft Edge TTS integration
- 18+ neural voices
- Audio generation and playback

### STT Module (STT.py)
- Multiple backends supported
- Web-based and Python-native
- Real-time transcription

## Browser Compatibility

| Browser | STT | TTS | Status |
|---------|-----|-----|--------|
| Chrome  | ✅  | ✅  | Full   |
| Edge    | ✅  | ✅  | Full   |
| Firefox | ⚠️  | ✅  | Limited|
| Safari  | ⚠️  | ✅  | Limited|

## Configuration

### Debug Mode
Set `DEBUG_MODE = true` in index.html for verbose logging.

### Voice Selection
Available voices defined in `TTS.py` VOICES dictionary.

## File Structure
```
├── index.html          # Main interface
├── tts_backend.py      # Local server
├── TTS.py             # Text-to-speech module
├── STT.py             # Speech-to-text module
├── api/
│   └── tts.py         # Vercel serverless function
├── css/               # Stylesheets
├── assets/            # Images and icons
└── audio/             # Generated audio files
```