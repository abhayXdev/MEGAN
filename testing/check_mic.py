import sounddevice as sd

print("Default input device:")
default = sd.query_devices(kind='input')
print(f"  {default['name']}")

print("\nAll input devices:")
for i, d in enumerate(sd.query_devices()):
    if d['max_input_channels'] > 0:
        marker = " (DEFAULT)" if d['name'] == default['name'] else ""
        print(f"  [{i}] {d['name']}{marker}")
