import locale
import random
from datetime import datetime, time
import os
import set_environment_vars
import re
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
    check_birthdays,
    delete_all_birthdays,
    remind_birthdays,
    remove_birthday,
    send_specific_birthday,
    show_birthday_list,
    stop_reminding_birthdays,
)
from components.const import status_messages, command_list
from components.schedule_callbacks import (
    remind_schedule,
    send_next_lesson,
    send_schedule,
    stop_reminding_schedule,
)
from components.utils import read_file, speech_to_text, text_to_speech, write_file

def start_command(update: Update, context: CallbackContext):
    """Welcomes the user and asks to send a voice message/command"""

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ciao! Posso ricordarti dei compleanni e delle materie di scuola,"
        " insieme a parecchie altre cose <i>utilissime</i> (tipo dirti che ore sono).\n"
        "Rispondo sia ai messaggi vocali che ai messaggi testuali.\n"
        "Per scoprire tutte le mie funzionalità puoi utilizzare /lista_comandi",
        parse_mode="HTML",
    )


def send_command_list(update: Update, context: CallbackContext):
    """Sends the user a list of commands and functionalities."""

    text = command_list
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML")


def help_command(update: Update, context: CallbackContext):
    """Sends the user a list of commands with their functions,
    as well as info on how to contact the developers."""
    
    text = (
        "Stai riscontrando un problema con il bot? Contatta uno sviluppatore."
        "\n • @gino_pincopallo \n • @Mattiiiaaa"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def text_file_to_speech(update: Update, context: CallbackContext):
    """Takes the text from the user's file and sends him an audio message
    which reads the text contained in the file"""
    text_file = update.message.document.get_file().download()
    text = read_file(text_file)
    voice_message = text_to_speech(text)
    with open(voice_message, "rb") as file:
        context.bot.send_voice(update.effective_chat.id, file)
    os.remove(voice_message)
    os.remove(text_file)


def speech_to_text_file(update: Update, context: CallbackContext):
    """Transcribes the voice message sent by the user into a txt file"""
    text = context.user_data["recognized_text"]
    text = text[15:]

    text_file = write_file(text)
    with open(text_file, "rb") as file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=file)
    os.remove(text_file)


def speech_to_text_message(update: Update, context: CallbackContext):
    """Transcribes the voice mesage sent by the user into a message."""
    text = context.user_data["recognized_text"]
    text = text[6:]
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


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
        [
            InlineKeyboardButton("Sì", callback_data="correct"),
            InlineKeyboardButton("No", callback_data="incorrect"),
        ],
    ]

    context.user_data["message"] = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(reply_markup),
    )


def confirm_handler(update: Update, context: CallbackContext):
    """Asks user to confirm if the text generated from the voice message is correct."""
    if update.callback_query.data == "incorrect":
        return

    handlers = {
        "scrivi su file": speech_to_text_file,
        "ripeti": speech_to_text_message,
        "come stai": status_handler,
        "che ore sono": send_time,
        "quando c'è": send_next_lesson,
        "quando compie gli anni": send_specific_birthday,
        "compie gli anni il ": add_birthday,
        "dimentica il compleanno di": remove_birthday,
        "mostrami i compleanni salvati": show_birthday_list,
        "ricordami dei compleanni salvati": remind_birthdays,
        "ricordami le materie": remind_schedule,
        "non ricordarmi le materie": stop_reminding_schedule,
        "aggiungi i compleanni della terza b s": add_known_birthdays,
        "elimina tutti i compleanni": delete_all_birthdays,
        r"ben|mal": user_status_handler,
    }

    transcribed_message = context.user_data["recognized_text"].lower()
    for activator, handler in handlers.items():
        activator = re.compile(activator)
        if activator.match(transcribed_message):
            # if activator in transcribed_message:
            handler(update, context)
    else:
        text="Non ho capito, consulta la /lista_comandi per vedere a cosa so rispondere."
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
def status_handler(update: Update, context: CallbackContext):
    """Tells user status of the bot and asks for user status"""
    text = status_messages[random.randint(0, len(status_messages) - 1)]
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


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


def unrecognized_message_handler(update: Update, context: CallbackContext):
    """Handles any message which wasn't caught by other handlers."""
    text = "n'agg capit"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def main():
    """Runs the bot"""
    locale.setlocale(locale.LC_ALL, "ita_ita")
    TOKEN = os.environ.get("TOKEN")

    persistence = PicklePersistence(filename="botpersistence")
    updater = Updater(token=TOKEN, persistence=persistence)
    job_queue = updater.job_queue
    job_queue.run_daily(callback=send_schedule, time=time(hour=14))
    job_queue.run_daily(callback=check_birthdays, time=time(hour=7))

    handlers = (
        MessageHandler(Filters.document, text_file_to_speech),
        CommandHandler("inizia", start_command),
        CommandHandler("help", help_command),
        CommandHandler("ricordami_compleanni", remind_birthdays),
        CommandHandler("aggiungi_compleanni_3BS", add_known_birthdays),
        CommandHandler("non_mi_ricordare_compleanni", stop_reminding_birthdays),
        CommandHandler("ricordami_materie", remind_schedule),
        CommandHandler("non_mi_ricordare_materie", stop_reminding_schedule),
        CommandHandler("lista_comandi", send_command_list),
        CommandHandler("compleanni_salvati", show_birthday_list),
        CommandHandler("elimina_compleanni", delete_all_birthdays),
        MessageHandler(Filters.regex(r"[Dd]imentica il compleanno di"), remove_birthday),
        MessageHandler(Filters.regex("[Cc]iao"), start_command),
        MessageHandler(Filters.document.category("audio/oga"), audio_message_handler),
        MessageHandler(Filters.voice, audio_message_handler),
        CallbackQueryHandler(add_known_birthdays, pattern="add known birthdays"),
        CallbackQueryHandler(confirm_handler, pattern="correct|incorrect"),
        MessageHandler(Filters.regex(r"[Qq]uando compie gli anni"), send_specific_birthday),
        MessageHandler(Filters.regex(r"compie gli anni il "), add_birthday),
        MessageHandler(Filters.regex(r"[Qq]uando c'è"), send_next_lesson),
        MessageHandler(Filters.regex(r"[Bb]en|[Mm]al|[Ss]chifo"),user_status_handler),
        MessageHandler(Filters.regex(r"[Cc]ome stai"), status_handler),
        MessageHandler(Filters.regex(r"[Cc]he ore sono"), send_time),
        MessageHandler(Filters.text, unrecognized_message_handler)
    )

    for handler in handlers:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
