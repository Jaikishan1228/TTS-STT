# 🎙️ TTS-STT Desktop Speech Suite

A **desktop-only** speech processing application combining **Speech-to-Text (STT)** and **Text-to-Speech (TTS)** using Microsoft Edge Neural voices and Web Speech API.

> **⚠️ Desktop Only**: Not compatible with mobile devices - requires desktop browsers for full functionality.

![Interface](assets/Screenshot%202025-09-26%20184031.png)

## ✨ Features

**🎤 Speech Recognition**
- Real-time speech transcription (50+ languages)
- Web Speech API integration
- Desktop microphone optimization

**🗣️ Neural Text-to-Speech** 
- 18+ Microsoft Edge Neural voices
- Multiple languages: English (US/UK/IN), Spanish, French, German
- Adjustable speed (0.5x-2.0x) and volume
- MP3 export capability

**🖥️ Desktop Interface**
- Professional dark theme
- Real-time visual feedback
- Browser compatibility: Chrome ✅, Edge ✅, Firefox ⚠️, Safari (TTS only)

## 🚀 Quick Start

### Local Setup (Recommended)
```bash
git clone https://github.com/Jaikishan1228/TTS-STT.git
cd TTS-STT
pip install -r requirements-local.txt
python tts_backend.py
# Open http://localhost:8000
```

### Cloud Setup (Basic TTS)
```bash
pip install -r requirements.txt
python tts_backend.py
```

**Live Demo**: [https://stt-tts-three.vercel.app](https://stt-tts-three.vercel.app)

## 🛠️ How It Works

### Speech-to-Text
Desktop Microphone → Web Speech API → Live Transcription → Text Output

### Text-to-Speech  
Text Input → Voice Selection → Edge Neural TTS → Audio/MP3

## 📁 Project Structure
```
├── index.html          # Web interface
├── tts_backend.py      # Local HTTP server
├── TTS.py             # Neural voice engine
├── STT.py             # Speech recognition
├── api/tts.py         # Vercel serverless function
└── requirements*.txt  # Dependencies
```

## 🔧 Browser Setup

| Browser | STT | TTS | Notes |
|---------|-----|-----|-------|
| Chrome  | ✅  | ✅  | Recommended |
| Edge    | ✅  | ✅  | Recommended |
| Firefox | ⚠️  | ✅  | Requires config* |
| Safari  | ❌  | ✅  | TTS only |
| Opera   | ❌  | ✅  | TTS only |

**Firefox Setup**: `about:config` → `media.webspeech.recognition.enable` → `true`

## 💻 Dependencies

**Core**: `edge-tts>=6.1.0`
**Local Development**: `pygame`, `SpeechRecognition`, `pyaudio`, `selenium`

## 🎯 Available Voices

**English**: Jenny, Guy, Aria, Davis (US) | Ryan, Sonia (UK) | Prabhat, Neerja (IN)
**Spanish**: Alvaro, Elvira
**French**: Henri, Denise  
**German**: Conrad, Katja

## 🔧 Troubleshooting

**STT Not Working?**
- Use Chrome/Edge browsers
- Check microphone permissions
- Firefox: Enable in about:config

**Audio Issues?**
- Check system volume
- Allow browser audio permissions
- Try different voices

## 🚀 Deployment

**Local**: Full features with Python backend
**Vercel**: Serverless TTS (STT via browser)
**Requirements**: Python 3.8+, Desktop browser

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Test on desktop browsers
4. Submit pull request

**Issues**: [GitHub Issues](https://github.com/Jaikishan1228/TTS-STT/issues)

## 📞 Support

- **Issues**: GitHub Issues
- **Email**: jaikishannishad33@gmail.com
- **Demo**: https://stt-tts-three.vercel.app

---

**🖥️ Built for Desktop • Neural TTS • Real-time STT**

[⭐ Star](https://github.com/Jaikishan1228/TTS-STT) • [🐛 Issues](https://github.com/Jaikishan1228/TTS-STT/issues) • **Made by [Jay](https://github.com/Jaikishan1228)**
