# MEGAN - Emotion-Aware Voice Assistant

<div align="center">

**An intelligent voice assistant that detects emotions from your speech and responds empathetically**

</div>

---

## 📖 Table of Contents
- [Overview](#-overview)
- [How It Works](#-how-it-works)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Technical Details](#-technical-details)

---

## 🌟 Overview

**MEGAN** (Emotion-Aware Voice Assistant) is a Python-based voice assistant that:
- **Listens** to your voice through your microphone
- **Detects** your emotional state (angry, happy, sad, or neutral)
- **Responds** intelligently using Google's Gemini AI
- **Speaks** back to you with text-to-speech
- **Adapts** responses based on your emotions

Unlike typical voice assistants, MEGAN understands *how* you say something, not just *what* you say, and adjusts responses accordingly.

---

## 🔬 How It Works

### 1. **Voice Input** (audio_handler.py)
   - Records 3 seconds of audio from your microphone (device 1)
   - Uses `sounddevice` to capture at 16kHz sample rate
   - Saves to temporary WAV file for processing
   - Uses Google Speech Recognition API to convert speech to text

### 2. **Emotion Detection** (emotion_detector.py)
   - Analyzes audio features:
     - **Energy**: Overall voice intensity
     - **Zero-Crossing Rate**: Pitch variation indicator
     - **Amplitude Variance**: Loudness changes
   - Classifies emotion using calibrated thresholds:
     - **Angry/Excited**: High energy (>0.0070) AND high amplitude variation (>0.080)
     - **Happy/Energetic**: Moderate energy (0.0045-0.0070) with variation (>0.050)
     - **Sad/Quiet**: Very low energy (<0.0030)
     - **Neutral**: Everything else

### 3. **AI Response** (gemini_client.py)
   - Sends your text + emotion context to Gemini AI (gemini-2.5-flash model)
   - System instruction makes Gemini emotion-aware:
     - Supportive and motivating when you're sad
     - Calming when you're angry
     - Enthusiastic when you're happy
     - Helpful when you're neutral

### 4. **Local Fallback** (local_responses.py)
   - If Gemini unavailable, uses built-in knowledge base:
     - Identity questions (who/what is MEGAN)
     - General knowledge (Virat Kohli, Einstein, Tesla, India facts)
     - Time/date queries
     - Emotion-aware greetings

### 5. **Voice Output** (text_to_speech.py)
   - Uses `pyttsx3` for text-to-speech
   - Isolated in subprocess to prevent repeated-use issues
   - Speaks responses back to you

---

## ✨ Features

✅ **Real-time emotion detection** from voice characteristics  
✅ **Intelligent AI responses** powered by Google Gemini  
✅ **Emotion-aware conversations** that adapt to your mood  
✅ **Voice input and output** for hands-free interaction  
✅ **Local fallback responses** when internet unavailable  
✅ **Modular architecture** for easy maintenance and extension  
✅ **Calibrated thresholds** based on actual voice data  
✅ **Windows PowerShell compatible**  

---

## 📁 Project Structure

```
megan/
├── megan.py              # Main entry point (100 lines)
├── audio_handler.py      # Microphone recording & speech recognition
├── emotion_detector.py   # Emotion analysis from audio features
├── gemini_client.py      # Google Gemini AI integration
├── text_to_speech.py     # Voice output functionality
├── local_responses.py    # Fallback responses & knowledge base
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── STRUCTURE.md         # Detailed architecture documentation
└── testing/             # Test scripts and backups
    ├── check_mic.py
    ├── check_models.py
    ├── test_mic.py
    ├── test_quick.py
    ├── tts_test.py
    └── megan_backup.py
```

---

## 🚀 Installation

### Prerequisites
- **Python 3.14** (or Python 3.10-3.13 for better library compatibility)
- **Windows** (tested on Windows 11)
- **Microphone** (built-in or external)
- **Internet connection** (for Gemini AI and speech recognition)

### Step 1: Clone or Download
```powershell
cd "C:\Users\YourName\Desktop"
# Download or extract the megan folder here
```

### Step 2: Create Virtual Environment
```powershell
cd megan
py -3 -m venv .venv
```

### Step 3: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Core dependencies:**
- `google-generativeai` - Gemini AI client
- `SpeechRecognition` - Speech-to-text
- `pyttsx3` - Text-to-speech
- `sounddevice` - Audio recording
- `numpy` - Numerical operations
- `scipy` - Signal processing

---

## 🎯 How to Run

### Quick Start
```powershell
# 1. Navigate to project folder
cd "C:\Users\Abhay Paul\Desktop\megan"

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Run MEGAN
python megan.py
```

### What You'll See
```
============================================================
  MEGAN - Emotion-Aware Voice Assistant
============================================================

I'm Megan! I can detect your emotions from your voice.
Say 'exit', 'quit', 'stop', or 'goodbye' to end the conversation.

[SUCCESS] Gemini AI connected with emotion-aware responses

You: Listening for 3 seconds...
[Audio level: max=15234, avg=3421.5]

You said: Hello, how are you today?
[Detected emotion: happy/energetic (energy=0.0061, zcr=0.078, amp_std=0.067)]

Megan: Hey! Love the positive energy! I'm doing great, thank you! 
       How can I help you today?

[Speaking...] [Done]
```

### Commands
- Say **"exit"**, **"quit"**, **"stop"**, or **"goodbye"** to end
- Press **Ctrl+C** to interrupt
- Speak clearly within 3 seconds after "Listening..." prompt

---

## ⚙️ Configuration

## ⚙️ Configuration

### Gemini API Key (Recommended)

MEGAN works best with Google Gemini AI. To enable it:

1. **Get API Key**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **Set Environment Variable** (Windows PowerShell):
   ```powershell
   $env:GEMINI_API_KEY = "your-api-key-here"
   ```
3. **Or edit gemini_client.py**: Replace the API key on line 19

Without Gemini, MEGAN uses local fallback responses (still functional but less intelligent).

### Microphone Settings

**Default**: Device 1 (Microphone Array)

To check available devices:
```powershell
python -c "import sounddevice as sd; print(sd.query_devices())"
```

To change device, edit `audio_handler.py` line 41:
```python
recording = sd.rec(..., device=1, ...)  # Change 1 to your device number
```

### Emotion Detection Thresholds

Thresholds in `emotion_detector.py` are calibrated for typical speaking voice:
- **Angry**: `energy > 0.0070 and amp_std > 0.080`
- **Happy**: `0.0045 < energy ≤ 0.0070 and amp_std > 0.050`
- **Sad**: `energy < 0.0030`

Adjust these if emotions aren't detected correctly for your voice.

---

## 🔧 Troubleshooting

### Problem: "Could not understand. Try again."
**Solution:**
- Speak louder and clearer
- Reduce background noise
- Check microphone is working: `testing\check_mic.py`
- Verify microphone permissions in Windows Settings

### Problem: No audio output (TTS silent)
**Solution:**
- Check Windows volume settings
- Verify default output device in Sound settings
- Test TTS: `python testing\tts_test.py`
- Try reinstalling pyttsx3: `pip install --force-reinstall pyttsx3`

### Problem: "Gemini unavailable, using local responses"
**Solution:**
- Set GEMINI_API_KEY environment variable (see Configuration)
- Check internet connection
- Verify API key is valid at [AI Studio](https://aistudio.google.com/)
- Check for API quota limits

### Problem: "ModuleNotFoundError"
**Solution:**
- Ensure virtual environment is activated: `.\.venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.10+)

### Problem: Audio level always low (max < 100)
**Solution:**
- Check microphone input level in Windows Settings → Sound → Input
- Try different microphone device (see Microphone Settings)
- Speak closer to microphone
- Test recording: `python testing\test_mic.py`

### Problem: Always detects "sad/quiet" emotion
**Solution:**
- Your voice might be naturally quieter
- Lower thresholds in `emotion_detector.py`:
  ```python
  if energy < 0.0020:  # Changed from 0.0030
      emotion = "sad/quiet"
  ```
- Speak with more energy to test detection

### Problem: Python 3.14 compatibility issues
**Solution:**
- Some packages (librosa, numba) don't support Python 3.14 yet
- Current implementation uses scipy instead (fully compatible)
- For advanced ML models, use Python 3.12:
  ```powershell
  py -3.12 -m venv .venv
  ```

---

## 🔬 Technical Details

### Emotion Detection Algorithm

MEGAN uses spectral analysis instead of deep learning for lightweight, real-time performance:

1. **Energy Calculation**:
   ```
   energy = Σ(amplitude²) / N
   ```
   Measures overall voice intensity

2. **Zero-Crossing Rate (ZCR)**:
   ```
   zcr = count(sign changes) / N
   ```
   Indicates pitch variation and voice quality

3. **Amplitude Standard Deviation**:
   ```
   amp_std = σ(|amplitude|)
   ```
   Measures loudness dynamics

4. **Classification**:
   - Multi-threshold decision tree
   - Calibrated on actual voice samples
   - ~75-85% accuracy for clear speech

### Why Not Deep Learning?

- **Speed**: Real-time processing without GPU
- **Compatibility**: Works on Python 3.14
- **Simplicity**: No model training or large files
- **Sufficient**: Good enough for conversational context

For research-grade accuracy, consider:
- SpeechBrain's emotion2vec
- Wav2Vec2 fine-tuned models
- OpenSMILE feature extraction + SVM

### System Architecture

```
User Voice Input
      ↓
[Sounddevice Recording] → 3s audio @ 16kHz
      ↓
[Temp WAV File] → Better recognition quality
      ↓
[Google Speech API] → Text transcription
      ↓
[Emotion Analyzer] → Feature extraction
      ↓
[Gemini AI] → Context + Emotion → Response
      ↓
[Text Cleaning] → Remove markdown
      ↓
[TTS Subprocess] → Voice output
      ↓
User Hears Response
```

### Module Dependencies

| Module | Dependencies | Purpose |
|--------|-------------|---------|
| audio_handler | sounddevice, numpy, scipy, SpeechRecognition | Audio I/O |
| emotion_detector | numpy | Feature extraction |
| gemini_client | google-generativeai | AI responses |
| text_to_speech | pyttsx3, sounddevice | Voice output |
| local_responses | datetime | Fallback logic |

---

## 📝 Usage Examples

### Example 1: Happy Greeting
```
You: Hey Megan, I got a promotion today!
[Detected emotion: happy/energetic]
Megan: That's fantastic! Congratulations on your promotion! 
       You must be so proud of your hard work paying off!
```

### Example 2: Sad Support
```
You: I'm feeling really down today...
[Detected emotion: sad/quiet]
Megan: I'm here for you. Remember, tough times don't last. 
       What can I do to help?
```

### Example 3: Angry De-escalation
```
You: This is so frustrating!
[Detected emotion: angry/excited]
Megan: I hear your intensity. Let's work through this together. 
       What would help right now?
```

### Example 4: Knowledge Query
```
You: Who is Virat Kohli?
[Detected emotion: neutral]
Megan: Virat Kohli is an Indian cricket captain and one of the 
       best batsmen in the world!
```

---

## 🚀 Future Enhancements

Potential improvements (contributions welcome):

- [ ] Multi-language support (Hindi, Spanish, etc.)
- [ ] Conversation history and context memory
- [ ] Custom wake word detection ("Hey Megan")
- [ ] Voice activity detection (auto-stop recording)
- [ ] Web interface or GUI
- [ ] Emotion visualization dashboard
- [ ] Integration with smart home devices
- [ ] Multi-user emotion profiles
- [ ] Advanced ML models (Wav2Vec2, emotion2vec)
- [ ] Cloud deployment options

---

## 📄 License

This project is open-source. Feel free to modify and distribute.

---

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent responses
- **Python Community** for excellent libraries
- **SciPy** for signal processing tools
- **OpenAI/Anthropic** for development assistance

---

## 📞 Support

Having issues? 

1. Check [Troubleshooting](#-troubleshooting) section
2. Review `STRUCTURE.md` for architecture details
3. Test individual components in `testing/` folder
4. Verify all dependencies installed: `pip list`

---

## 🎓 Learn More

- [Google Gemini Documentation](https://ai.google.dev/docs)
- [Speech Recognition Guide](https://github.com/Uberi/speech_recognition)
- [Audio Signal Processing Basics](https://en.wikipedia.org/wiki/Audio_signal_processing)
- [Emotion Recognition Research](https://arxiv.org/abs/2203.07378)

---

<div align="center">

**Made with ❤️ by Abhay Paul**

*MEGAN - Understanding not just what you say, but how you feel*

</div>
