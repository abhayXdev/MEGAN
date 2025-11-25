"""
Emotion Detector Module
Analyzes audio to detect emotional state
"""
import io
import wave
import struct

try:
    import numpy as np
except:
    np = None


def analyze_emotion_from_audio(audio) -> str:
    """Extract spectral features for emotion classification.
    Accepts either numpy array (from sounddevice) or AudioData object.
    """
    if audio is None:
        return "unknown"

    try:
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
        # Calibrated thresholds - adjusted for better sensitivity
        
        # Angry/Excited: Higher energy OR strong amplitude variation
        if (energy > 0.0040 and amp_std > 0.045) or energy > 0.0080:
            emotion = "angry/excited"
        # Happy/Energetic: Moderate energy range
        elif energy > 0.0020 and energy <= 0.0040 and amp_std > 0.025:
            emotion = "happy/energetic"
        # Sad/Quiet: Very low energy
        elif energy < 0.0015:
            emotion = "sad/quiet"
        else:
            emotion = "neutral"

        return emotion + f" (energy={energy:.4f}, zcr={zcr:.3f}, amp_std={amp_std:.3f})"
    except Exception as e:
        return f"unknown (error: {e})"
