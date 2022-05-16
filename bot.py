from datetime import datetime
import locale
import time
from os import environ
import random


from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

import set_environment_vars
from bot_data import day_of_week, materie, statuses
from bot_utils import append_to_csv, edit_csv, read_csv, speech_to_text, read_file

TOKEN = environ.get("TOKEN")
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


locale.setlocale(locale.LC_ALL, "ita_ita")


def start_command(update: Update, context: CallbackContext):
    """Welcomes the user and asks to send a voice message/command

    Args:
        update (Update): _description_
        context (CallbackContext): _description_
    """

    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Ciao! Puoi mandarmi un vocale o un messaggio e io ti risponderò."\
            "Per scoprire tutte le mie funzionalità puoi utilizzare /command_list"
    )


def send_command_list(update: Update, context: CallbackContext):
    """Sends the user a list of commans and functionalities.

    Args:
        update (Update): update
        context (CallbackContext): _description_
    """
    
    text = """Ecco un elenco delle mie funzionalità:\n
        - con il comando /ricordami_lezioni, ogni giorno ti invierò una lista
            con le materie del mattino seguente.\n
        - con il comando /ricordami_compleanni, ti invierò una notifica ogni
            volta che è il compleanno di uno dei tuoi compagni.\n
        - per aggiungere qualcuno alla lista di compleanni, invia un vocale
            o un messaggio contenente le parole "Nome Cognome compie gli anni il DD/MM"
        - per sapere la prossima lezione di una materia specifica 
            chiedimi (tramite vocale o messaggio) "Quando c\'è lezione di ___?"
        - per sapere come sto chiedimi "come stai"
        - se mandi un file posso leggerlo a voce alta
        - per farmi scrivere, in un file, ciò che hai detto (in un vocale) pronuncia "trascrivi file" all'inizio del vocale
        - per farmi scrivere, sullo schermo, ciò che hai detto (in un vocale) pronuncia "trascrivi schermo" all'inizio del vocale
        - per sapere che ore sono chiedimi (tramite vocale o messaggio) "che ore sono" o "che ora è"
            """
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def help_command(update: Update, context: CallbackContext):
    """Sends the user a list of commands with their functions,
    as well as info on how to contact the developers."""

    text = "Stai riscontrando un problema con il bot? Puoi contattare gli sviluppatori 💻!" \
        "\n • @gino_pincopallo\n • @id_telegram_mattia"
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def file_handler(update: Update, context: CallBackContext):

    file_name = update.file.get_file().download()
    text = read_file(file_name)
    audio_message = text_to_speech(text)
    context.bot.send_voice(chat_id=update.effective_chat.id, audio_message)
    

def audio_message_handler(update: Update, context: CallbackContext):
    """Handles any voice message received by the bot, after analizing its content
    it asks the user if it has understood correctly.

    Args:
        update (Update): update
        context (CallbackContext): context
    """

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="TYPING")

    file_name = update.message.voice.get_file().download()
    context.user_data["recognized_text"] = speech_to_text(file_name)

    recognized_text = context.user_data["recognized_text"]
    text = f'"{recognized_text}"\nè corretto?'

    reply_markup = [
        [InlineKeyboardButton("Sì", callback_data="correct")],
        [InlineKeyboardButton("No", callback_data="incorrect")],
    ]

    context.user_data["message"] = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(reply_markup),
    )


def confirm_handler(update: Update, context: CallbackContext):
    """Asks user to confirm if the text generated from the voice message is correct.

    Args:
        update (Update): update
        context (CallbackContext): context
    """

    if update.callback_query.data == "incorrect":
        text = "Non ho capito bene, ripeti perfavore."
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    user_message = context.user_data["recognized_text"].lower()
    if "come stai" in user_message:
        status_handler(update, context)
    elif "che ore sono" in user_message or "che ora è" in user_message:
        send_time(update, context)
    elif "quando c'è" in user_message:
        send_next_lesson(update, context)
    elif "compie gli anni" in user_message:
        add_birthday(update, context)
    elif "compleanno" in user_message:
        find_birthday(update, context)
    else:
        text = "Boh avevi detto che avevo capito bene ma non mi pare proprio, ripeti grazie"


def status_handler(update: Update, context: CallbackContext):
    """Tells user status of the bot and asks for user status

    Args:
        update (Update): _description_
        context (CallbackContext): _description_
    """
    text = statuses[random.randint(0,len(statuses) - 1)]

    
def file_handler(update: Update, context: CallBackContext):
    ogg_file_name = oga_file_name.replace("oga", "ogg")
    os.rename(oga_file_name, ogg_file_name)

    pydub.AudioSegment.from_ogg(ogg_file_name).export()
    audio_segment = pydub.AudioSegment.from_ogg(ogg_file_name)
    audio_segment.export("converted_file.wav", "wav")

    os.remove(ogg_file_name)
    file_name = update.file.get_file().download()
    text = read_file(file_name)
    audio_message = text_to_speech(text)
    context.bot.send_voice(chat_id=update.effective_chat.id, audio_message)
    
    
def answer_handler(update: Update, context: CallbackContext):
    """Sends the user a different message according to their answer to the previous question.

    Args:
        update (Update): update
        context (CallbackContext): context
    """
    user_message = update.message.text
    if "bene" in user_message.lower():
        text = ":)"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    if "male" in user_message.lower():
        text = ":("
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def send_time(update: Update, context: CallbackContext):
    """Sends the user the current time.

    Args:
        update (Update): update
        context (CallbackContext): context
    """
    current_time = f"sono le: {datetime.now().strftime('%h:m')}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=current_time)


def send_next_lesson(update: Update, context: CallbackContext):
    """Sends the user a message containing info on when the next lesson is.

    Args:
        update (Update): update
        context (CallbackContext): context
    """
    text = ""
    user_message = update.message.text.split()
    for key, value in materie.items():
        value = value.split("•")
        for subject in value:
            if user_message[2] in subject:
                time, subject = subject.split()
                text = f"{day_of_week[key]} alle {time}"
                break
    if not text:
        text = f"{user_message[2]} non esiste"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def add_birthday(update: Update, context: CallbackContext, **kwargs):
    """Adds birthday to the csv file containing the registered birthdays.
    Args:
        update (Update): update
        context (CallbackContext): context
    kwargs:
        from_audio (Bool): True
    """

    user_message = update.message.text.split()
    name = user_message[0]
    surname = user_message[1]
    birthday = user_message[6]

    if kwargs.get("from_audio"):
        birthday = f"{user_message[6]} {user_message[7]}"
        text = f"Ok! Il {birthday} ti ricorderò del compleanno di {name} {surname}"
        try:
            birthday = time.strptime(birthday, "%d %B").strftime("%d/%m")
        except ValueError:
            text = (
                "Non credo di aver capito bene, potresti ripetere? Per aggiungere un compleanno"
                " a quelli che ti devo ricordare manda un vocale/scrivi un messaggio"
                ' dove dici "Nome Cognome compie gli anni il giorno mese"'
            )

    if name.isalpha() and surname.isalpha() and birthday[:2].isnumeric():
        data = read_csv("birthdays.csv")

        index = None
        for dictionary in data:
            if dictionary["Nome"] == f"{name} {surname}":
                text = f"Il compleanno di {name} {surname} è già stato registrato."
                if dictionary["Data"] == birthday:
                    text += f"Ho modificato il compleanno da {dictionary['Data']} a {birthday}"
                    index = data.index(dictionary)
                break

        if index:
            data[index]["Data"] = birthday
            edit_csv("birthdays.csv", data)
        else:
            append_to_csv("birthdays.csv", f"{name} {surname},{birthday}\n")

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

 
def find_birthday(update: Update, context: CallBackContext):
    user_message = user_message = update.message.text.split()
    person = user_message[1] + " " + user_message[2]
    data = read_csv("birthday.csv")
    for x in data:
        if x["Nome"] == person:
            birthday = time.strptime(x["Data"], "%d %m").strftime("%d/%B")
            text = f"{x["Nome"]} compie gli anni il {birthday}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            break



def unrecognized_message_handler(update: Update, context: CallbackContext):
    """Handles any message which wasn't caught by the other handlers.

    Args:
        update (Update): update
        context (CallbackContext): context
    """

    text = "n'agg capit"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def main():
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("command_list", send_command_list))
    dispatcher.add_handler(MessageHandler(Filters.voice, audio_message_handler))
    dispatcher.add_handler(
        CallbackQueryHandler(confirm_handler, pattern="correct|incorrect")
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"compie gli anni il \d\d/\d\d"), add_birthday)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"Quando c'è"), send_next_lesson)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"bene|male|benissimo|uno schifo"), answer_handler)
    )

    dispatcher.add.handler(MessageHandler(Filters.regex(r"[Cc]he ore sono|[Cc]he ora è"),send_time))

    dispatcher.add_handler(MessageHandler(Filters.text, unrecognized_message_handler))
    updater.start_polling()


if __name__ == "__main__":
    main()
