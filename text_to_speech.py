"""
Text-to-Speech Module
Handles voice output
"""
import subprocess
import sys
import time

try:
    import sounddevice as sd
except:
    sd = None

try:
    import pyttsx3
    tts_available = True
except:
    pyttsx3 = None
    tts_available = False


def speak(text, max_length=500):
    """Speak the given text using TTS"""
    if not tts_available:
        return False
        
    try:
        print("[Speaking...]", end="", flush=True)
        
        # Stop any sounddevice streams before TTS
        if sd is not None:
            try:
                sd.stop()
            except:
                pass
        
        time.sleep(0.3)
        
        # Split long responses into chunks if needed
        speak_text = text
        if len(text) > max_length:
            speak_text = text[:max_length] + "..."
        
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
            return False
        else:
            print(" [Done]")
        
        # Pause to ensure audio device is fully released
        time.sleep(0.8)
        return True
    except Exception as e:
        print(f"\nTTS error: {e}")
        return False


def speak_goodbye():
    """Speak goodbye message"""
    if not tts_available:
        return
        
    try:
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
