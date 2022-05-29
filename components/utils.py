from datetime import datetime
import os
import speech_recognition
import pydub
import pyttsx3


def convert_oga_to_wav(oga_file_name: str) -> str:
    """Converts .oga audio file into .wav audio file, returns converted file name.
    Args:
        oga_file_name (str): oga_file_name
    Returns:
        str: wav_file_name
    """

    ogg_file_name = oga_file_name.replace("oga", "ogg")
    os.rename(oga_file_name, ogg_file_name) # Renames file from .oga to .ogg

    # Creates an AudioSegment Object from the ogg file
    audio_segment = pydub.AudioSegment.from_ogg(ogg_file_name)
    audio_segment.export("converted_file.wav", "wav") # Creates new wav file from that AudioSegment

    os.remove(ogg_file_name) # Removes the unused ogg file
    return "converted_file.wav" # Returns converted file name


def speech_to_text(oga_file_name: str) -> str:
    """Returns the audio file's content converted into text (powered by Google)
    Args:
        file_oga_name (str): oga_file_name
    Returns:
        str: text
    """
    
    recognizer = speech_recognition.Recognizer()
    recognizer.energy_threshold = 300 # Sets minimum energy threshold to improve recogntion
    converted_file = convert_oga_to_wav(oga_file_name) # Converts oga file to wav file
    audio_file = speech_recognition.AudioFile(converted_file) # Creates AudioFile object

    with audio_file as source: # Opens AudioFile object as source
        audio_data = recognizer.record(source) # Creates AudioData object from source
    try:
        # Sends AudioData to Google's speech recognition API
        text = recognizer.recognize_google(audio_data, language="it-IT")  
    except speech_recognition.UnknownValueError: # Handles error if no speech is recognized
        text = ""
    os.remove("converted_file.wav") # Removes the unused wav file
    return text


def text_to_speech(text: str) -> None:
    """Converts text into a .oga audio file, using window's default voice.
    Returns converted file name

    Args:
        text (str): text_to_convert
    """

    engine = pyttsx3.init() # Creates new TTS enginge instance
    # Sets synthetic voice to microsoft's Elsa
    engine.setProperty(
        "voice",
        "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_IT-IT_ELSA_11.0",
    )
    engine.save_to_file(text, "output_message.oga") # Saves the audio file as output_message.oga 
    engine.stop() # Stops the engine
    return "output_message.oga"


def read_file(filename: str):
    """Returns the text contained in the given txt file

    Args:
        filename (str): any
    """

    with open(filename, "r") as file:
        text = file.read()
        return text


def write_file(text):
    """Writes text to a file and returns its name.

    Args:
        text (_type_): text to write in the file

    Returns:
        str: output file name
    """

    with open("text_file.txt", "w") as file:
        file.write(text)
        return "text_file.txt"


def time_delta(lst):
    """Helper function which calculates how many days remain until the given date

    Args:
        lst (list): DD/MM str at index 1

    Returns:
        int: number of days to the date at index 1
    """

    date = lst[1] # gets the date from the list
    # Creates a datetime object with the given date's day and month and current year
    date = datetime.strptime(date, "%d/%m").date().replace(year=datetime.now().year)
    current_date = datetime.now().date()
    # If the date has passed, it adds (or rather subtracts) the days which have passed to 365
    if date < current_date:
        return 365 + (date - datetime.now().date()).days
    return (date - current_date).days


if __name__ == "__main__":
    print("Questo file contiene solo funzioni")
