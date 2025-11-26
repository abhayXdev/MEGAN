import re
import os
import sys
import argparse
import io
import wave
import struct
import math

# Non-fatal dependency checks: record availability and continue with fallbacks
missing_deps = []
genai = None
pyttsx3 = None
sr = None
sd = None
np = None

try:
    import google.generativeai as _genai
    genai = _genai
except Exception:
    missing_deps.append("google-generative-ai (pip install google-generative-ai)")

try:
    import pyttsx3 as _pyttsx3
    pyttsx3 = _pyttsx3
except Exception:
    missing_deps.append("pyttsx3 (pip install pyttsx3)")

try:
    import speech_recognition as _sr
    sr = _sr
except Exception:
    missing_deps.append("SpeechRecognition (pip install SpeechRecognition)")

try:
    import sounddevice as _sd
    sd = _sd
except Exception:
    # sounddevice is optional; we'll fall back to text input if missing
    pass

try:
    import numpy as _np
    np = _np
except Exception:
    pass

if missing_deps:
    print("\n[WARNING] Missing Python dependencies (falling back where possible):\n")
    for dep in missing_deps:
        print(f"  - {dep}")
    print("\nYou can create a venv and install requirements with:\n")
    print("  py -3 -m venv .venv")
    print("  .\\.venv\\Scripts\\activate")
    print("  py -3 -m pip install -r requirements.txt\n")


# ---------------- Text Cleaning Function -----------------
def clean_text(text):
    text = re.sub(r'[*#`]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ---------------- Voice / Text Input Function -----------------
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

        # 1) Try speech_recognition microphone if available
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
                    
                    # Use device 1 (default microphone) instead of 0
                    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=1, blocking=True)
                    sd.wait()
                    
                    # Check recording volume
                    max_amplitude = np.max(np.abs(recording))
                    avg_amplitude = np.mean(np.abs(recording))
                    print(f"[Audio level: max={max_amplitude}, avg={avg_amplitude:.1f}]")
                    
                    if max_amplitude < 100:
                        print(f"[WARNING] Very low audio volume detected. Speak louder or check your microphone.")
                    
                    # Save audio to temporary file for better recognition
                    import tempfile
                    from scipy.io import wavfile
                    
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
                # Microphone not usable (PyAudio missing or device error)
                pass

        # 2) Fallback to text input after max attempts
        if attempts >= max_attempts:
            if text_fallback:
                print("\nSwitching to text input...")
                txt = input(prompt)
                return txt, None
            raise RuntimeError("No available audio input method")


def analyze_emotion_from_audio(audio) -> str:
    """Extract spectral features for emotion classification.
    Uses scipy signal processing for spectral analysis.
    Accepts either numpy array (from sounddevice) or AudioData object.
    """
    if audio is None:
        return "unknown"

    try:
        from scipy.fft import dct
        from scipy.signal import get_window
        
        # Handle different audio input types
        if isinstance(audio, np.ndarray):
            # Direct numpy array from sounddevice (int16)
            audio_array = audio.flatten().astype('float32') / 32768.0
            framerate = 16000  # Default sample rate
        else:
            # AudioData object from speech_recognition
            wav_bytes = audio.get_wav_data()
            with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
                n_channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                frames = wf.readframes(n_frames)

            # Unpack samples (assume 16-bit PCM)
            if sampwidth == 2:
                fmt = '<{n}h'.format(n=(len(frames) // 2))
                samples = struct.unpack(fmt, frames)
            else:
                samples = list(frames)

            # If stereo, take only one channel
            if n_channels == 2:
                samples = samples[::2]

            # Convert to numpy array and normalize
            audio_array = np.array(samples, dtype='float32') / 32768.0
        
        N = len(audio_array)
        if N == 0:
            return "unknown"
        
        # Calculate energy and pitch variation
        energy = np.sum(audio_array ** 2) / N
        
        # Calculate zero-crossing rate (pitch variation indicator)
        zero_crossings = 0
        for i in range(1, N):
            if (audio_array[i] >= 0 and audio_array[i-1] < 0) or (audio_array[i] < 0 and audio_array[i-1] >= 0):
                zero_crossings += 1
        zcr = zero_crossings / N
        
        # Calculate amplitude variance (loudness changes)
        amp_std = np.std(np.abs(audio_array))
        
        # Classify emotion based on energy, pitch variation, and amplitude dynamics
        # Calibrated thresholds based on actual voice analysis
        
        # Angry/Excited: Higher energy OR strong amplitude variation
        if (energy > 0.0070 and amp_std > 0.080) or energy > 0.0150:
            emotion = "angry/excited"
        # Happy/Energetic: Moderate energy range
        elif energy > 0.0045 and energy <= 0.0070 and amp_std > 0.050:
            emotion = "happy/energetic"
        # Sad/Quiet: Very low energy
        elif energy < 0.0030:
            emotion = "sad/quiet"
        else:
            emotion = "neutral"

        return emotion + f" (energy={energy:.4f}, zcr={zcr:.3f}, amp_std={amp_std:.3f})"
    except Exception as e:
        return f"unknown (error: {e})"



# ---------------- Gemini API Setup (optional) -----------------
API_KEY = os.getenv("GEMINI_API_KEY", "your_api_key_here")
genai_available = False
if genai is None:
    print("[WARNING] Gemini client not available; responses will be local fallback.")
else:
    if not API_KEY:
        print("[WARNING] GEMINI_API_KEY not set. Gemini responses disabled.")
    else:
        try:
            genai.configure(api_key=API_KEY)
            # Create model with system instruction for emotion-aware responses
            system_instruction = (
                "You are Megan (spelled M-E-G-A-N), an empathetic voice assistant. "
                "ALWAYS remember: Your name is Megan. "
                "You respond based on the user's emotional state detected from their voice. "
                "When the user is sad/quiet: be supportive, motivating, and encouraging. "
                "When angry/excited: be calming and understanding. "
                "When happy/energetic: match their enthusiasm. "
                "When neutral: be helpful and friendly. "
                "Keep responses concise (2-3 sentences). "
                "If asked about your name, mention that you are Megan, an emotion-aware voice assistant."
            )
            model = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=system_instruction
            )
            chat = model.start_chat(history=[])
            genai_available = True
            print("[SUCCESS] Gemini AI connected with emotion-aware responses")
        except Exception as e:
            print("⚠️  Could not initialize Gemini client:", e)
            genai_available = False


# ---------------- Text-to-Speech Setup (optional) -----------------
tts_available = False
engine = None
if pyttsx3 is not None:
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        voices = engine.getProperty("voices")
        if len(voices) > 1:
            engine.setProperty("voice", voices[1].id)
        tts_available = True
    except Exception:
        tts_available = False

print("Gemini Voice Assistant (say 'exit' to quit)\n")


# ---------------- Main Loop -----------------
def local_responder(text: str, emotion: str = "neutral") -> str:
    """Emotion-aware fallback responder when Gemini isn't available."""
    t = text.lower()
    
    # Extract base emotion
    base_emotion = emotion.split('(')[0].strip() if '(' in emotion else emotion
    
    # Emotion-aware prefixes
    if "angry" in base_emotion or "excited" in base_emotion:
        prefix = "I hear your intensity. "
    elif "sad" in base_emotion or "quiet" in base_emotion:
        prefix = "I'm here for you. "
    elif "happy" in base_emotion or "energetic" in base_emotion:
        prefix = "Love the energy! "
    else:
        prefix = ""
    
    # Answer specific questions
    if "who" in t or "what" in t or "when" in t or "where" in t or "why" in t or "how" in t:
        # Questions - acknowledge we're limited
        if "who are you" in t or "what are you" in t or "who r u" in t or "hu r u" in t:
            return prefix + "I'm Megan, your emotion-aware voice assistant! I listen to your voice and respond based on how you're feeling."
        elif "your name" in t or "what is your name" in t:
            return prefix + "My name is Megan - I'm your voice assistant who understands emotions!"
        elif "who created you" in t or "who made you" in t or "who developed you" in t or "your creator" in t or "your developer" in t:
            return prefix + "I'm an AI assistant designed to understand and respond to emotions in your voice."
        elif "virat kohli" in t:
            return prefix + "Virat Kohli is an Indian cricket captain and one of the best batsmen in the world!"
        elif "nikola tesla" in t or "tesla" in t:
            return prefix + "Nikola Tesla was a brilliant Serbian-American inventor and engineer, famous for his work on electricity and AC power systems!"
        elif "einstein" in t or "albert einstein" in t:
            return prefix + "Albert Einstein was a genius physicist who developed the theory of relativity and the famous equation E=mc²!"
        elif "india" in t and "capital" in t:
            return prefix + "The capital of India is New Delhi!"
        elif "pm of india" in t or "prime minister of india" in t:
            return prefix + "The Prime Minister of India is Narendra Modi!"
        elif "weather" in t:
            return prefix + "I can't check the weather right now, but you can ask Google or check weather apps!"
        elif "your name" in t:
            return prefix + "My name is Meggan - I'm your voice assistant that understands emotions!"
        elif "what can you do" in t or "what do you do" in t:
            return prefix + "I can chat with you, detect your emotions from your voice, and respond accordingly! Try talking in different tones."
        elif "time" in t:
            from datetime import datetime
            return prefix + "Current time is " + datetime.now().strftime("%H:%M:%S")
        elif "date" in t:
            from datetime import datetime
            return prefix + "Today is " + datetime.now().strftime("%B %d, %Y")
        else:
            return prefix + "That's an interesting question! I'm a simple assistant, so I might not know everything, but I'm here to chat with you!"
    
    # Greetings
    if any(g in t for g in ["hello", "hi", "hey"]):
        if "sad" in base_emotion or "quiet" in base_emotion:
            return "Hey there! I'm here for you. Things will get better. What's on your mind?"
        elif "angry" in base_emotion or "excited" in base_emotion:
            return "Hello! I sense you're feeling intense. Let's talk it through. What's going on?"
        elif "happy" in base_emotion or "energetic" in base_emotion:
            return "Hey! Love the positive energy! What can I do for you today?"
        else:
            return "Hello! How can I help you today?"
    
    # Check feelings
    if "how are you" in t or "how r u" in t:
        return prefix + "I'm doing well, thank you! More importantly, how are YOU feeling?"
    
    if "angry" in t or "mad" in t:
        return prefix + "I'm not angry at all! I'm here to help you. What's bothering you?"
    
    # Default with emotion awareness
    if "sad" in base_emotion or "quiet" in base_emotion:
        return "I'm listening and I care. Remember, tough times don't last. What can I do to help?"
    elif "angry" in base_emotion or "excited" in base_emotion:
        return "I hear you. Let's work through this together. What would help right now?"
    elif "happy" in base_emotion or "energetic" in base_emotion:
        return "That's awesome! I'm excited to chat with you! What's on your mind?"
    else:
        return "I'm here to chat with you. What would you like to talk about?"


def main():
    global genai_available  # Allow modification of global variable
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-voice", action="store_true", help="Force text input/output (no microphone/speech)")
    args = parser.parse_args()

    while True:
        try:
            prompt = "Speak: " if not args.no_voice else "You: "
            use_voice = not args.no_voice
            user_input, audio = listen_and_recognize(prompt, use_voice=use_voice)
            print(user_input)

            # Check for exit commands first (before emotion analysis)
            if user_input.strip().lower() in ["exit", "quit", "bye", "stop"]:
                print("\nAssistant: Goodbye!")
                if tts_available:
                    try:
                        import subprocess, sys, time
                        if sd is not None:
                            try:
                                sd.stop()
                            except:
                                pass
                        time.sleep(0.3)
                        tts_code = '''
import pyttsx3
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)
engine.say("Goodbye! Have a nice day.")
engine.runAndWait()
engine.stop()
'''
                        subprocess.run([sys.executable, "-c", tts_code], capture_output=True, timeout=10)
                    except:
                        pass
                break

            # If we captured audio, analyze emotion and show it
            emotion = "neutral"
            if audio is not None:
                emotion = analyze_emotion_from_audio(audio)
                print("Emotion:", emotion)
        except KeyboardInterrupt:
            print("\n\nAssistant: Goodbye!")
            if tts_available and engine is not None:
                try:
                    engine.say("Goodbye!")
                    engine.runAndWait()
                except:
                    pass
            break

        # Get reply either from Gemini or local fallback
        emotion_str = emotion if audio is not None else "neutral"
        
        # Extract base emotion (remove metrics in parentheses)
        base_emotion = emotion_str.split('(')[0].strip() if '(' in emotion_str else emotion_str
        
        if genai_available:
            try:
                # Include emotion context in the prompt
                emotion_context = f"[User emotion: {base_emotion}] "
                full_prompt = emotion_context + user_input
                response = chat.send_message(full_prompt)
                reply_text = clean_text(response.text)
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    print("[WARNING] Gemini API quota exceeded. Using local responses.")
                    genai_available = False
                elif "404" in error_msg:
                    # Model not found - disable Gemini and use local responses
                    genai_available = False
                else:
                    print("Gemini error:", e)
                reply_text = local_responder(user_input, emotion_str)
        else:
            reply_text = local_responder(user_input, emotion_str)

        print("Assistant:", reply_text)
        if tts_available:
            try:
                print("[Speaking...]", end="", flush=True)
                
                # Stop any sounddevice streams before TTS
                if sd is not None:
                    try:
                        sd.stop()
                    except:
                        pass
                
                # Wait a bit before starting TTS
                import time
                import subprocess
                import sys
                
                time.sleep(0.3)
                
                # Split long responses into chunks if needed
                speak_text = reply_text
                if len(reply_text) > 500:
                    speak_text = reply_text[:500] + "..."
                
                # Use subprocess to run TTS in isolation
                tts_code = f'''
import pyttsx3
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)
engine.say({repr(speak_text)})
engine.runAndWait()
engine.stop()
'''
                
                # Run TTS in separate process
                result = subprocess.run(
                    [sys.executable, "-c", tts_code],
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    print(f"\n[TTS error: {result.stderr.decode()}]")
                else:
                    print(" [Done]")
                
                # Longer pause to ensure audio device is fully released
                time.sleep(0.8)
            except Exception as e:
                print(f"\nTTS error: {e}")


if __name__ == "__main__":
    main()
