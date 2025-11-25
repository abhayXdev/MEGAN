import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyCxKF6VZRKcHVO_NNEPQ6nRpKQ-aUL3-_A'

import google.generativeai as genai
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

print("Available Gemini models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")
