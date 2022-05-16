import os
import csv
import speech_recognition
import pydub
import pyttsx3

recognizer = speech_recognition.Recognizer()


def convert_oga_to_wav(oga_file_name) -> str:
    """Converts .oga audio file into .wav audio file.
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


def speech_to_text(oga_file_name) -> str:
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

    text = recognizer.recognize_google(audio_data, language="it-IT")

    os.remove("converted_file.wav")
    return text


def text_to_speech(text) -> None:
    """Converts text into a .oga audio file, using window's default voice
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


def read_csv(filename) -> list:
    """Returns a list of dictionaries extrapolated from the csv file.
    Args:
        filename (_type_): _description_
    Returns:
        list: _description_
    """
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        data = []
        for dictionary in reader:
            data.append(dictionary)
    return data


def edit_csv(filename: str, data: dict):
    """Rewrites the csv file with the modified data.
    Args:
        filename (str): any
        new_data (dict): any
    """
    with open(filename, "w") as file:
        writer = csv.DictWriter(file, fieldnames=["Nome", "Data"])
        writer.writeheader()
        for line in data:
            file.writerow(line)


def append_to_csv(filename: str, newline: str):
    """Adds a new line to the csv file.
    Args:
        filename (str): _description_
        newline (str): _description_
    """

    with open(filename, "a") as file:
        file.write(newline)


if __name__ == "__main__":

    text_to_speech("ciao")
