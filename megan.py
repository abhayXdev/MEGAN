#!/usr/bin/env python3
"""
MEGAN - Emotion-Aware Voice Assistant
Main entry point that orchestrates all modules
"""
import sys

# Import modules
from audio_handler import listen_and_recognize
from emotion_detector import analyze_emotion_from_audio
from gemini_client import GeminiClient
from text_to_speech import speak, speak_goodbye, tts_available
from local_responses import get_response as local_responder


def clean_text(text):
    """Remove markdown formatting from text"""
    import re
    text = re.sub(r'[*#`]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def main():
    """Main conversation loop"""
    # Initialize Gemini client
    gemini_client = GeminiClient()
    gemini_available = gemini_client.available
    
    print("\n" + "="*60)
    print("  MEGAN - Emotion-Aware Voice Assistant")
    print("="*60)
    print("\nI'm Megan! I can detect your emotions from your voice.")
    print("Say 'exit', 'quit', 'stop', or 'goodbye' to end the conversation.\n")
    
    if not tts_available:
        print("[WARNING] Text-to-speech not available. Responses will be text-only.\n")
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input, audio = listen_and_recognize()
            if not user_input:
                continue
            
            user_input = user_input.strip()
            if not user_input:
                continue
            
            # Check for exit commands BEFORE emotion analysis to avoid audio glitches
            lower_input = user_input.lower()
            if any(cmd in lower_input for cmd in ["exit", "quit", "stop", "goodbye", "bye"]):
                print("\nMegan: Goodbye! Have a nice day.")
                if tts_available:
                    speak_goodbye()
                break
            
            # Analyze emotion from audio
            emotion = "neutral"
            if audio is not None:
                emotion = analyze_emotion_from_audio(audio)
                print(f"[Detected emotion: {emotion}]")
            
            # Get response
            response_text = None
            
            # Try Gemini first if available
            if gemini_available:
                response_text = gemini_client.send_message(user_input, emotion)
                if response_text is None:
                    # Gemini failed, disable for this session and use fallback
                    gemini_available = False
                    print("[Gemini unavailable, using local responses]")
                    response_text = local_responder(user_input, emotion)
            else:
                # Use local responder
                response_text = local_responder(user_input, emotion)
            
            # Clean and display response
            response_text = clean_text(response_text)
            print(f"\nMegan: {response_text}\n")
            
            # Speak response
            if tts_available:
                speak(response_text)
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            if tts_available:
                speak_goodbye()
            break
        except Exception as e:
            print(f"\nError in main loop: {e}")
            continue


if __name__ == "__main__":
    main()
