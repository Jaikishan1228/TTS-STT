# 🎙️ Speech Processing Suite

A modern, full-featured web application that combines **Speech-to-Text (STT)** and **Text-to-Speech (TTS)** capabilities with neural voice synthesis and real-time speech recognition.

![Speech Processing Suite Interface](assets/Screenshot%202025-09-26%20184031.png)

## ✨ Key Features

🎤 **Advanced Speech Recognition**
- Real-time speech transcription with live feedback
- Support for 50+ languages and dialects
- Web Speech API integration for high accuracy
- Automatic noise suppression and ambient adjustment

🗣️ **Premium Neural Voices**
- 18+ Microsoft Edge Neural TTS voices
- Multiple accents: US, UK, Indian, Spanish, French, German
- Adjustable speech rate and volume controls
- High-quality MP3 audio export

🌐 **Modern Web Interface**
- Professional dark theme with responsive design
- Real-time visual feedback and status indicators
- Mobile-friendly touch controls
- Progressive Web App capabilities

🔧 **Browser Compatibility**
- Enhanced cross-browser support (Chrome, Edge, Firefox, Safari)
- Automatic feature detection and fallbacks
- Intelligent error handling with user guidance
- Browser-specific optimizations for best performance

☁️ **Flexible Deployment**
- Local development server included
- One-click Vercel deployment ready
- Serverless function support
- Cross-platform compatibility

**🎯 Crafted with ❤️ by Jay | [Live Demo](https://tts-stt-ivory.vercel.app)**

## 🚀 Quick Start

### Local Development (Full Features)
```bash
# Clone the repository
git clone https://github.com/Jaikishan1228/TTS-STT.git
cd TTS-STT

# Install ALL dependencies for local development
pip install -r requirements-local.txt

# Start the local server
python tts_backend.py

# Open http://localhost:8000
```

### Quick Setup (TTS Only)
```bash
# For basic TTS functionality only
pip install -r requirements.txt
python tts_backend.py
```

### 🌐 Live Demo
**[Access the app here: https://tts-stt-ivory.vercel.app](https://tts-stt-ivory.vercel.app)**

The production deployment is automatically updated when changes are pushed to the main branch. The app uses Vercel's serverless functions with a minimal `requirements.txt` containing only `edge-tts` for TTS functionality. Full STT features work through the browser's Web Speech API, requiring no server-side dependencies.

## 🎯 How It Works

### 🎤 Speech-to-Text Flow
```
Microphone Input → Web Speech API → Real-time Transcription → Text Output
```
- Click **"Start Recording"** to begin speech recognition
- Speak clearly into your microphone
- Watch real-time transcription appear in the text area
- Use **"Stop Recording"** to finish or **"Clear"** to reset

### 🗣️ Text-to-Speech Flow  
```
Text Input → Voice Selection → Neural Processing → Audio Generation → MP3 Download
```
- Enter or paste text in the **"Text to Convert"** area
- Choose from **18+ premium neural voices**
- Adjust **speech rate** (0.5x - 2.0x) and **volume** (0% - 100%)
- Click **"Speak Text"** for playback or **"Save Audio"** for MP3 download

### ⚙️ Available Voices
| Language | Male Voices | Female Voices |
|----------|-------------|---------------|
| **English (US)** | Guy, Davis, Jason, Tony | Jenny, Aria, Jane, Sara |
| **English (UK)** | Ryan | Sonia |
| **English (India)** | Prabhat | Neerja |
| **Spanish (Spain)** | Alvaro | Elvira |
| **French (France)** | Henri | Denise |
| **German (Germany)** | Conrad | Katja |

## 🛠️ Technical Architecture

### System Design
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│  Python Backend  │◄──►│   Edge-TTS API  │
│  (Frontend UI)  │    │ (HTTP Server)    │    │ (Voice Engine)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   Real-time UI          Audio Processing        Neural Synthesis
```

### 📁 Project Structure
```
TTS-STT/
├── 🌐 index.html              # Main web interface
├── 🐍 tts_backend.py          # Local development server
├── 🎤 STT.py                  # Speech recognition engine
├── 🗣️ TTS.py                  # Text-to-speech engine
├── 📁 api/
│   └── tts.py                 # Vercel serverless function
├── 📁 assets/
│   ├── icons8-favorite-48.png # Favicon
│   └── Screenshot...png       # UI preview
├── 📁 css/                    # Styling (4 optimized files)
├── 📁 fonts/                  # Web typography
├── 📁 audio/                  # Generated audio files
├── ⚙️ vercel.json             # Vercel deployment config
├── 📋 requirements.txt        # Python dependencies
├── 🔐 .gitignore              # Git exclusions
└── 📖 README.md               # This documentation
```

### 🔧 Core Dependencies
| Package | Purpose | Version |
|---------|---------|---------|
| `edge-tts` | Neural voice synthesis | ≥6.1.0 |
| `pygame` | Audio playback & mixing | Latest |
| `speech_recognition` | Python STT engine | ≥3.10.0 |
| `selenium` | Browser automation | ≥4.15.0 |

## � Development Guide

### Local Development Setup
```bash
# Install Python 3.8+ and pip
python --version

# Clone and setup
git clone https://github.com/Jaikishan1228/TTS-STT.git
cd TTS-STT

# Install dependencies (choose one)
pip install -r requirements.txt         # Basic TTS only
pip install -r requirements-local.txt   # Full development features

# Run local server
python tts_backend.py
# Server starts at http://localhost:8000

# For development with auto-reload
# (Optional) Use nodemon or similar tools
```

### 🌐 Browser Compatibility
| Browser | STT Support | TTS Support | Status | Notes |
|---------|------------|-------------|---------|-------|
| **Chrome** | ✅ Full | ✅ Full | Recommended | Best performance |
| **Edge** | ✅ Full | ✅ Full | Recommended | Native Windows integration |
| **Firefox** | ⚠️ Manual Setup | ✅ Full | Partial | Requires `about:config` setup |
| **Safari** | ⚠️ iOS Only | ✅ Full | Limited | Desktop STT not supported |
| **Opera** | ❌ Not Supported | ✅ Full | TTS Only | Use Chrome/Edge for STT |

> **Firefox Setup**: Enable speech recognition in `about:config` → set `media.webspeech.recognition.enable` to `true`  
> **Opera Users**: Speech recognition is not supported. Voice synthesis works normally.

### 🔧 Python API Usage
```python
# Text-to-Speech Example
from TTS import TextToSpeech

# Initialize TTS with specific voice
tts = TextToSpeech(voice='en-US-JennyNeural')

# Speak text aloud
tts.speak("Hello! Welcome to Speech Processing Suite.")

# Save as MP3 file
tts.save_audio("This will be saved as audio", "my_speech.mp3")

# List all available voices
TextToSpeech.list_voices()
```

```python
# Speech-to-Text Example  
from STT import WebSTT

# Initialize STT with language
stt = WebSTT(language='en-US')

# Listen for speech input
text = stt.listen()
print(f"You said: {text}")

# Close when done
stt.close()
```

## 🌟 Features Showcase

### 🎯 Real-time Speech Recognition
- **Instant Feedback**: Live transcription as you speak
- **Language Support**: 50+ languages including English, Spanish, French, German, Hindi, Chinese
- **Noise Filtering**: Automatic background noise suppression
- **Mobile Ready**: Touch-friendly controls for mobile devices

### 🎭 Premium Neural Voices  
- **Studio Quality**: Microsoft Edge Neural TTS technology
- **Natural Speech**: Human-like intonation and pronunciation
- **Customizable**: Adjustable speech rate (0.5x - 2.0x) and volume
- **Export Ready**: High-quality MP3 downloads

### 🚀 Deployment Options
- **Local Development**: Instant setup with Python server
- **Vercel Production**: One-click serverless deployment
- **Cross-Platform**: Windows, macOS, Linux support
- **Mobile Responsive**: Works perfectly on smartphones and tablets

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
4. **Make** your changes and test thoroughly
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to your branch (`git push origin feature/amazing-feature`)
7. **Submit** a Pull Request with a clear description

### � Bug Reports & Feature Requests
- Use [GitHub Issues](https://github.com/Jaikishan1228/TTS-STT/issues) to report bugs
- Clearly describe the issue with steps to reproduce
- For feature requests, explain the use case and expected behavior

## 🙏 Acknowledgments

- **Microsoft Edge TTS** - For providing high-quality neural voice synthesis
- **Web Speech API** - For enabling browser-based speech recognition  
- **Python Community** - For excellent libraries and frameworks
- **Open Source Contributors** - For inspiration and collaborative spirit

## 📞 Support & Contact

- 🐛 **Issues**: [GitHub Issues](https://github.com/Jaikishan1228/TTS-STT/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Jaikishan1228/TTS-STT/discussions)
- 📧 **Contact**: [jaikishannishad33@gmail.com](mailto:jaikishannishad33@gmail.com)

---

<div align="center">

**🎙️ Speech Processing Suite**

*Transforming voice interactions with cutting-edge technology*

**Made with ❤️ by [Jay](https://github.com/Jaikishan1228)**

[⭐ Star this repo](https://github.com/Jaikishan1228/TTS-STT) • [🐛 Report Bug](https://github.com/Jaikishan1228/TTS-STT/issues) • [✨ Request Feature](https://github.com/Jaikishan1228/TTS-STT/issues)

</div>