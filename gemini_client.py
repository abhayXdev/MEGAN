"""
Gemini AI Client Module
Handles Gemini API interaction
"""
import os

try:
    import google.generativeai as genai
except:
    genai = None


class GeminiClient:
    def __init__(self, api_key=None):
        self.available = False
        self.chat = None
        self.model = None
        
        if genai is None:
            print("[WARNING] Gemini client not available; responses will be local fallback.")
            return
            
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "AIzaSyB7uf373-HPFTCZUlDW0PBoGzD9zNruZhM")
        
        if not self.api_key:
            print("[WARNING] GEMINI_API_KEY not set. Gemini responses disabled.")
            return
            
        try:
            genai.configure(api_key=self.api_key)
            
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
            
            self.model = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=system_instruction
            )
            self.chat = self.model.start_chat(history=[])
            self.available = True
            print("[SUCCESS] Gemini AI connected with emotion-aware responses")
        except Exception as e:
            print(f"[WARNING] Could not initialize Gemini client: {e}")
            self.available = False
    
    def send_message(self, message, emotion="neutral"):
        """Send message to Gemini with emotion context"""
        if not self.available:
            return None
            
        try:
            # Extract base emotion (remove metrics in parentheses)
            base_emotion = emotion.split('(')[0].strip() if '(' in emotion else emotion
            
            # Include emotion context in the prompt
            emotion_context = f"[User emotion: {base_emotion}] "
            full_prompt = emotion_context + message
            
            response = self.chat.send_message(full_prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print("[WARNING] Gemini API quota exceeded. Using local responses.")
                self.available = False
            elif "404" in error_msg:
                # Model not found - disable Gemini
                self.available = False
            else:
                print(f"Gemini error: {e}")
            return None
