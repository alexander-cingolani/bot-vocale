import os
import speech_recognition
import pydub
import pyttsx3
recognizer = speech_recognition.Recognizer()


def convert_oga_to_wav(oga_file_name):
    """Converts .oga file into .wav file.

    Args:
        oga_file_name (str): oga_file_name

    Returns:
        str: wav_file_name
    """
    
    file_ogg_name = oga_file_name.replace("oga", "ogg")
    os.rename(oga_file_name, file_ogg_name)
    
    audio_segment = pydub.AudioSegment.from_ogg(file_ogg_name)
    audio_segment.export("converted_file.wav", "wav")
    os.remove(file_ogg_name)
    return "converted_file.wav"


def speech_to_text(oga_file_name):
    """Sends query to google services which returns the audio file's content converted into text

    Args:
        file_oga_name (str): oga_file_name

    Returns:
        str: text
    """

    converted_file = convert_oga_to_wav(oga_file_name)
    audio_file = speech_recognition.AudioFile(converted_file)
    with audio_file as source:
        audio_data = recognizer.record(source)

    text = recognizer.recognize_google(audio_data, language="it-IT")

    os.remove("converted_file.wav")
    return text


def speech_to_text(text):
    """Converts the text received as argument into a .oga file

    Args:
        text (str): text_to_convert
    """
    engine = pyttsx3.init()
    engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_IT-IT_ELSA_11.0")
    engine.save_to_file(text, "output_message.oga")
    engine.runAndWait()
    
    
if __name__ == "__main__":
    print(speech_to_text("audio-prova.ogg"))
    speech_to_text("oggi c'è informatica")
    