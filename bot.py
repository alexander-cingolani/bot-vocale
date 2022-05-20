import locale
import random
from datetime import datetime, time
from os import environ

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    PicklePersistence,
    Updater,
)

from components.birthday_callbacks import (
    add_birthday,
    add_known_birthdays,
    remind_birthdays,
    remove_birthday,
    send_specific_birthday,
)
from components.const import status_messages
from components.schedule_callbacks import (
    check_subjects,
    remind_schedule,
    send_next_lesson,
)
from components.utils import read_file, speech_to_text, text_to_speech


def start_command(update: Update, context: CallbackContext):
    """Welcomes the user and asks to send a voice message/command"""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ciao! Posso ricordarti di compleanni e delle materie di scuola,"
        " insieme a parecchie altre cose <i>utilissime</i> (tipo dirti che ore sono)."
        "Rispondo sia a messaggi vocali che a messaggi testuali."
        "Per scoprire tutte le mie funzionalità puoi utilizzare /command_list",
    )


def send_command_list(update: Update, context: CallbackContext):
    """Sends the user a list of commands and functionalities."""

    text = """
<b>Comandi testuali:</b>
/ricordami_lezioni - Ti invierò giornalmente la lista delle materie del mattino seguente.
/ricordami_compleanni - Ti ricorderò dei compleanni che aggiungi.

<b>Comandi vocali:</b>
<i>"Trascrivi ..."</i> per trascrivere il vocale in un file di testo.

<b>Comandi vocali e testuali:</b>
<i>"Nome Cognome compie gli anni il DD/MM"</i> per ricordarti di un compleanno.
<i>"Dimentica il compleanno di Nome Cognome"</i> per non ricevere più una notifica quando compie gli anni.
<i>"Quando compie gli anni Nome Cognome"</i> per sapere il giorno del compleanno di qualcuno
<i>"Quando c\'è lezione di _____?"</i> per sapere la prossima volta che c'è quella materia.
<i>"Come stai?"</i> per sapere come sto.
<i>"Che ore sono"</i> per sapere che ore sono

Se invii un file di testo ti invierò un vocale dove lo leggo ad alta voce.
"""
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
    )


def help_command(update: Update, context: CallbackContext):
    """Sends the user a list of commands with their functions,
    as well as info on how to contact the developers."""

    text = (
        "Stai riscontrando un problema con il bot? Puoi contattare gli sviluppatori 💻!"
        "\n • @gino_pincopallo\n • @id_telegram_mattia"
    )

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def file_handler(update: Update, context: CallbackContext):
    """Takes the text from the user's file and sends him a voice message
    which reads the text contained in the file"""

    file_name = update.file.get_file().download()
    text = read_file(file_name)
    audio_message = text_to_speech(text)
    context.bot.send_voice(chat_id=update.effective_chat.id, text=audio_message)


def speech_to_text_file(update: Update, context: CallbackContext):
    """Transcribes the voice message sent by the user into a txt file
    he writes it in a file"""

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="TYPING")

    file_name = update.message.voice.get_file().download()
    recognized_text = speech_to_text(file_name)

    # ANCORA LO DEVO FINIRE
    # Ricorda di eliminare la prima parola che sarà "trascrivi"


def audio_message_handler(update: Update, context: CallbackContext):
    """Handles any voice message received by the bot, after analizing its content
    it asks the user if it has understood correctly."""

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="TYPING")
    file_name = update.message.voice.get_file().download()
    recognized_text = speech_to_text(file_name)
    if not recognized_text:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hai detto qualcosa? Non ti ho sentito.",
        )
        return
    context.user_data["recognized_text"] = recognized_text

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
    """Asks user to confirm if the text generated from the voice message is correct."""

    if update.callback_query.data == "incorrect":
        text = "Non ho capito bene, ripeti perfavore."
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    transcribed_message = context.user_data["recognized_text"].lower()
    if "trascrivi" in transcribed_message[:9]:
        speech_to_text_file(update, context)
    elif "come stai" in transcribed_message:
        status_handler(update, context)
    elif "che ore sono" in transcribed_message or "che ora è" in transcribed_message:
        send_time(update, context)
    elif "quando c'è" in transcribed_message:
        send_next_lesson(update, context)
    elif "compie gli anni" in transcribed_message:
        add_birthday(update, context, from_audio=True)
    elif "compleanno" in transcribed_message:
        send_specific_birthday(update, context)
    elif "dimentica" in transcribed_message:
        remove_birthday(update, context, from_audio=True)
    else:
        text = "Temo di non aver capito, puoi ripetere perfavore?."
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def status_handler(update: Update, context: CallbackContext):
    """Tells user status of the bot and asks for user status"""

    text = status_messages[random.randint(0, len(status_messages) - 1)]
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def text_file_to_speech(update: Update, context: CallbackContext):
    """Takes the text from the user's file and sends him an audio message
    which reads the text contained in the file"""

    file_name = update.file.get_file().download()
    text = read_file(file_name)
    voice_message = text_to_speech(text)

    context.bot.send_voice(update.effective_chat.id, voice_message)


def user_status_handler(update: Update, context: CallbackContext):
    """Sends the user a different message according to their answer to the previous question."""

    try:
        user_message = update.message.text.lower()
    except AttributeError:
        user_message = context.user_data["recognized_text"].lower()

    if "ben" in user_message or "ok" in user_message:
        text = ":)"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    if "mal" in user_message.lower() or "schifo" in user_message:
        text = ":("
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def send_time(update: Update, context: CallbackContext):
    """Sends the user the current time."""

    current_time = f"Sono le {datetime.now().strftime('%H:%M')}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=current_time)


def check_birthdays(context: CallbackContext):
    """Checks if the current date corresponds to any birthday saved by a user."""

    today = datetime.now().date().strftime("%d/%m")
    for registered_user in context.bot_data:
        for name, birthday in registered_user["Birthdays"].items():
            if birthday == today:
                text = f"Oggi è il compleanno di {name}, fagli gli auguri!"
                context.bot.send_message(chat_id=registered_user, text=text)


def unrecognized_message_handler(update: Update, context: CallbackContext):
    """Handles any message which wasn't caught by other handlers."""

    text = "n'agg capit"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def main():
    """Runs the bot"""

    locale.setlocale(locale.LC_ALL, "ita_ita")
    TOKEN = environ.get("TOKEN")

    persistence = PicklePersistence(filename="botpersistence")
    updater = Updater(token=TOKEN, persistence=persistence)
    job_queue = updater.job_queue

    dispatcher = updater.dispatcher
    job_queue.run_daily(callback=check_subjects, time=time(hour=21))
    job_queue.run_daily(callback=check_birthdays, time=time(hour=15, minute=59))
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("ricordami_compleanni", remind_birthdays))
    dispatcher.add_handler(CommandHandler("ricordami_materie", remind_schedule))
    dispatcher.add_handler(CommandHandler("command_list", send_command_list))
    dispatcher.add_handler(
        MessageHandler(Filters.text("Dimentica il compleanno di"), remove_birthday)
    )
    dispatcher.add_handler(MessageHandler(Filters.regex("[Cc]iao"), start_command))
    dispatcher.add_handler(MessageHandler(Filters.voice, audio_message_handler))
    dispatcher.add_handler(
        MessageHandler(Filters.document.category("audio/oga"), audio_message_handler)
    )
    dispatcher.add_handler(
        CallbackQueryHandler(add_known_birthdays, pattern="add known birthdays")
    )
    dispatcher.add_handler(
        CallbackQueryHandler(confirm_handler, pattern="correct|incorrect")
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(r"[Qq]uando compie gli anni"), send_specific_birthday
        )
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"compie gli anni il \d\d/\d\d"), add_birthday)
    )

    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"[Qq]uando c'è"), send_next_lesson)
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(r"[Bb]ene|[Mm]ale|[Bb]enissimo|[Ss]chifo|ok"),
            user_status_handler,
        )
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"[Cc]ome stai"), status_handler)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"[Cc]he ore sono|[Cc]he ora è"), send_time)
    )
    dispatcher.add_handler(MessageHandler(Filters.text, unrecognized_message_handler))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
