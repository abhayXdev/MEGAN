# MEGAN - Modular Structure

## Overview
The voice assistant has been reorganized into a clean modular structure.

## File Structure

```
megan/
├── megan.py              # Main entry point (100 lines)
├── audio_handler.py       # Microphone recording & speech recognition
├── emotion_detector.py    # Emotion analysis from voice
├── gemini_client.py       # Gemini AI integration
├── text_to_speech.py      # Voice output functionality
├── local_responses.py     # Fallback responses
├── requirements.txt       # Dependencies
├── README.md             # Documentation
└── testing/              # Test and backup files
    ├── check_mic.py
    ├── check_models.py
    ├── test_mic.py
    ├── test_quick.py
    ├── tts_test.py
    └── megan_backup.py  # Original monolithic version
```

## Module Descriptions

### 1. **megan.py** (Main Entry Point - 100 lines)
- Orchestrates all modules
- Main conversation loop
- User input/output handling
- Exit command processing

### 2. **audio_handler.py**
- Microphone recording using sounddevice (device 1)
- 3-second audio capture at 16kHz
- Temporary WAV file creation for better recognition
- Google Speech API integration
- Fallback to text input if voice unavailable

### 3. **emotion_detector.py**
- Audio feature extraction (energy, zero-crossing rate, amplitude variance)
- Calibrated emotion thresholds:
  - Angry/Excited: energy > 0.0070 & amp_std > 0.080
  - Happy/Energetic: 0.0045 < energy ≤ 0.0070 & amp_std > 0.050
  - Sad/Quiet: energy < 0.0030
  - Neutral: everything else
- Returns emotion with metrics

### 4. **gemini_client.py**
- Gemini API configuration (gemini-2.5-flash)
- System instruction with emotion-aware behavior
- Chat session management
- Error handling and fallback flags
- Identity: "Megan" - emotion-aware voice assistant

### 5. **text_to_speech.py**
- pyttsx3 TTS integration
- Subprocess isolation for repeated use
- Voice rate and volume configuration
- Audio device cleanup before speech
- Goodbye message function

### 6. **local_responses.py**
- Fallback responses when Gemini unavailable
- Emotion-aware response prefixes
- Knowledge base:
  - Identity questions (name, creator)
  - General knowledge (Virat Kohli, Tesla, Einstein, India facts)
  - Time/date queries
  - Greetings
- Context-aware defaults based on emotion

## How to Run

```powershell
# Activate virtual environment
.\.venv\Scripts\activate

# Run the assistant
python megan.py
```

## Module Dependencies

- **audio_handler**: speech_recognition, sounddevice, numpy, scipy
- **emotion_detector**: numpy
- **gemini_client**: google-generativeai
- **text_to_speech**: pyttsx3, sounddevice
- **local_responses**: datetime (built-in)

## Benefits of Modular Structure

1. **Maintainability**: Each module has a single responsibility
2. **Readability**: Main file reduced from 515 lines to 100 lines
3. **Testability**: Modules can be tested independently
4. **Extensibility**: Easy to add new features or swap implementations
5. **Reusability**: Modules can be used in other projects
6. **Organization**: Related functionality grouped together

## Configuration

All calibrated settings are preserved:
- Microphone device: 1 (Microphone Array)
- Audio sample rate: 16kHz
- Recording duration: 3 seconds
- Emotion thresholds: Calibrated from actual voice analysis
- Gemini model: gemini-2.5-flash
- API key: Configured in gemini_client.py

## Testing

Original monolithic version backed up to `testing/megan_backup.py`

All modules successfully import and function correctly.
