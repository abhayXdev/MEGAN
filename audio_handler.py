"""
Audio Handler Module
Handles microphone recording and speech recognition
"""
import tempfile
from scipy.io import wavfile

try:
    import speech_recognition as sr
except:
    sr = None

try:
    import sounddevice as sd
except:
    sd = None

try:
    import numpy as np
except:
    np = None


def listen_and_recognize(prompt="You: ", text_fallback=True, use_voice=True):
    """Listen using microphone and return (transcript, audio_data).
    Falls back to text input returning (text, None) if SpeechRecognition or microphone not available.
    """
    # If voice is disabled, go straight to text input
    if not use_voice:
        txt = input(prompt)
        return txt, None
    
    # Use a loop instead of recursion. Try SR microphone, then sounddevice VAD, then text input.
    attempts = 0
    max_attempts = 3
    while True:
        attempts += 1

        # Try speech_recognition microphone if available
        if sr is not None:
            try:
                # Use sounddevice to record since PyAudio is missing
                if sd is not None and np is not None:
                    print(prompt, end="", flush=True)
                    print("Listening for 3 seconds...")
                    
                    duration = 3
                    fs = 16000
                    
                    # Stop any audio playback before recording
                    try:
                        sd.stop()
                    except:
                        pass
                    
                    # Use device 1 (default microphone)
                    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=1, blocking=True)
                    sd.wait()
                    
                    # Check recording volume
                    max_amplitude = np.max(np.abs(recording))
                    avg_amplitude = np.mean(np.abs(recording))
                    print(f"[Audio level: max={max_amplitude}, avg={avg_amplitude:.1f}]")
                    
                    if max_amplitude < 100:
                        print(f"[WARNING] Very low audio volume detected. Speak louder or check your microphone.")
                    
                    # Save audio to temporary file for better recognition
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                        wavfile.write(temp_wav.name, fs, recording)
                        temp_filename = temp_wav.name
                    
                    r = sr.Recognizer()
                    r.energy_threshold = 10
                    r.dynamic_energy_threshold = False
                    
                    try:
                        with sr.AudioFile(temp_filename) as source:
                            audio_data = r.record(source)
                        text = r.recognize_google(audio_data, language='en-US')
                        print(f"\nYou said: {text}")
                        
                        # Clean up temp file
                        try:
                            import os
                            os.unlink(temp_filename)
                        except:
                            pass
                        
                        return text, recording
                    except sr.UnknownValueError:
                        print("\nCould not understand. Try again.")
                        if attempts >= max_attempts:
                            pass  # Fall through to text input
                        else:
                            continue
                    except sr.RequestError as e:
                        print(f"\nSpeech service error: {e}")
                        if attempts >= max_attempts:
                            pass
                        else:
                            continue
                else:
                    # sounddevice not available, skip SR method
                    pass
            except Exception as e:
                print(f"\nRecognition error: {e}")
                pass

        # Fallback to text input after max attempts
        if attempts >= max_attempts:
            if text_fallback:
                print("\nSwitching to text input...")
                txt = input(prompt)
                return txt, None
            raise RuntimeError("No available audio input method")
