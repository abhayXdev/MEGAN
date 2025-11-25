import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.say('This is a quick test. If you hear this, T T S is working.')
engine.runAndWait()
print('TTS test completed')
