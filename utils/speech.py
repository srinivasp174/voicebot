import speech_recognition as sr
from gtts import gTTS
import time
import uuid

def transcribe(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

def text(text, filename=None):
    if filename is None:
        # Generate unique filename using timestamp and UUID
        timestamp = str(int(time.time()))
        unique_id = str(uuid.uuid4())[:8]
        filename = f"response_{timestamp}_{unique_id}.mp3"
    
    tts = gTTS(text)
    tts.save(filename)
    return filename
