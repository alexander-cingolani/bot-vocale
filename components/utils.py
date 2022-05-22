from datetime import datetime
import os
import speech_recognition
import pydub
import pyttsx3

recognizer = speech_recognition.Recognizer()


def convert_oga_to_wav(oga_file_name: str) -> str:
    """Converts .oga audio file into .wav audio file, returns converted file name.
    Args:
        oga_file_name (str): oga_file_name
    Returns:
        str: wav_file_name
    """
    ogg_file_name = oga_file_name.replace("oga", "ogg")
    os.rename(oga_file_name, ogg_file_name)

    pydub.AudioSegment.from_ogg(ogg_file_name).export()
    audio_segment = pydub.AudioSegment.from_ogg(ogg_file_name)
    audio_segment.export("converted_file.wav", "wav")

    os.remove(ogg_file_name)

    return "converted_file.wav"


def speech_to_text(oga_file_name: str) -> str:
    """Returns the audio file's content converted into text (powered by Google)
    Args:
        file_oga_name (str): oga_file_name
    Returns:
        str: text
    """
    converted_file = convert_oga_to_wav(oga_file_name)
    audio_file = speech_recognition.AudioFile(converted_file)

    with audio_file as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language="it-IT")
    except speech_recognition.UnknownValueError:
        text = ""
    os.remove("converted_file.wav")
    return text


def text_to_speech(text: str) -> None:
    """Converts text into a .oga audio file, using window's default voice.
    Returns converted file name

    Args:
        text (str): text_to_convert
    """

    engine = pyttsx3.init()

    # Selects italian voice from windows
    engine.setProperty(
        "voice",
        "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_IT-IT_ELSA_11.0",
    )
    engine.save_to_file(text, "output_message.oga")
    engine.runAndWait()
    return "output_message.oga"


def read_file(filename: str):
    """Returns the text contained in the given txt file

    Args:
        filename (str): any
    """
    with open(filename, "r") as file:
        text = file.read()
        return text


def time_delta(item):
    date = item[1]
    date = datetime.strptime(date, "%d/%m").date().replace(year=datetime.now().year)
    if date < datetime.now().date():
        return 365 + (date - datetime.now().date()).days
    return (date - datetime.now().date()).days

if __name__ == "__main__":
    print("Questo file contiene solo funzioni")
    print(time_delta("20/05"))