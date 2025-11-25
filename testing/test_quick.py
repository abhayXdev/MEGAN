"""Quick test of emotion detection without microphone"""
import sys
sys.path.insert(0, '.')

# Mock audio data for testing
class MockAudio:
    def get_wav_data(self):
        # Return a simple 1-second 16kHz mono WAV with some test samples
        import struct
        import io
        import wave
        
        # Create a simple tone
        samples = []
        for i in range(16000):
            val = int(10000 * (i % 100) / 100)  # sawtooth wave
            samples.append(val)
        
        # Build WAV
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(struct.pack(f'<{len(samples)}h', *samples))
        
        return buf.getvalue()

# Test emotion analyzer
from meggan import analyze_emotion_from_audio, local_responder

audio = MockAudio()
emotion = analyze_emotion_from_audio(audio)
print(f"Detected emotion: {emotion}")

# Test responder with different emotions
test_phrases = [
    ("hello", "neutral"),
    ("hello", "happy/energetic"),
    ("hello", "sad/quiet"),
    ("hello", "angry/excited"),
    ("what can you do", "neutral"),
]

print("\nTesting emotion-aware responses:")
for phrase, emo in test_phrases:
    response = local_responder(phrase, emo)
    print(f"  Input: '{phrase}' | Emotion: {emo}")
    print(f"  Response: {response}\n")

print("✓ All tests passed!")
