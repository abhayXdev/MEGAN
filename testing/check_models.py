import os
os.environ['GEMINI_API_KEY'] = 'paste your api here'

import google.generativeai as genai
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

print("Available Gemini models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")
