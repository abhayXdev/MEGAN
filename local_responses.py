"""
Local Responses Module
Fallback responses when Gemini is not available
"""
from datetime import datetime


def get_response(text: str, emotion: str = "neutral") -> str:
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
        # Identity questions
        if "who are you" in t or "what are you" in t or "who r u" in t or "hu r u" in t:
            return prefix + "I'm Megan, your emotion-aware voice assistant! I listen to your voice and respond based on how you're feeling."
        elif "your name" in t or "what is your name" in t:
            return prefix + "My name is Megan - I'm your voice assistant who understands emotions!"
        elif "who created you" in t or "who made you" in t or "who developed you" in t or "your creator" in t or "your developer" in t:
            return prefix + "I'm an AI assistant designed to understand and respond to emotions in your voice."
        
        # General knowledge questions
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
        elif "what can you do" in t or "what do you do" in t:
            return prefix + "I can chat with you, detect your emotions from your voice, and respond accordingly! Try talking in different tones."
        elif "time" in t:
            return prefix + "Current time is " + datetime.now().strftime("%H:%M:%S")
        elif "date" in t:
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
