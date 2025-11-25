import sounddevice as sd
import numpy as np
import time

print("Testing microphone...")
print("Speak now for 3 seconds...")

# Record 3 seconds
duration = 3
fs = 16000

try:
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=0, blocking=True)
    print("Recording...")
    sd.wait()
    print("Done recording!")
    
    # Calculate RMS to see if we captured sound
    arr = recording.reshape(-1).astype('float32')
    rms = float(np.sqrt(np.mean(arr ** 2)))
    
    print(f"\nRMS Energy: {rms:.2f}")
    if rms > 10:
        print("✓ Microphone is working! Sound detected.")
    else:
        print("✗ No sound detected. Microphone might not be working or is too quiet.")
    
    # Show max value
    max_val = np.max(np.abs(arr))
    print(f"Max amplitude: {max_val:.2f}")
    
except Exception as e:
    print(f"Error: {e}")
