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

import set_environment_vars
from components.birthday_callbacks import (
    add_birthday,
    add_known_birthdays,
    check_birthdays,
    remind_birthdays,
    remove_birthday,
    send_specific_birthday,
    show_birthday_list,
    stop_reminding_birthdays,
)
from components.const import status_messages
from components.schedule_callbacks import (
    remind_schedule,
    send_next_lesson,
    send_schedule,
    stop_reminding_schedule,
)
from components.utils import read_file, speech_to_text, text_to_speech


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

    text = """
<b>Comandi testuali: (Hanno tutti una controparte vocale)</b>
/ricordami_materie - Ti invierò giornalmente la lista delle materie del mattino seguente.
/non_mi_ricordare_materie - Smetterò di ricordarti delle tue materie.
/ricordami_compleanni - Ti ricorderò dei compleanni che aggiungi e che aggiungerai.
/non_mi_ricordare_compleanni - Smetterò di ricordarti dei compleanni.
/compleanni_salvati - Visualizza i compleannni salvati dal più vicino al più lontano.
/aggiungi_compleanni_3BS - Aggiungerò i compleanni della 3BS ai tuoi compleanni salvati.
/lista_comandi - Ti invierò questa lista.
/help - Ti invierò informazioni su come contattare gli sviluppatori in caso di problemi.

<b>Comandi vocali:</b>
<i>"Trascrivi su file ..."</i> - Trascriverò ciò che hai detto in un file di testo.
<i>"Ripeti ..."</i> - Ripeterò ciò che hai detto in un messaggio
<i>"Ricordami dei compleanni salvati"</i> - Ti ricorderò dei compleanni che hai aggiunto
e che aggiungerai.
<i>"Ricordami le materie"</i> - Ogni giorno ti invierò la lista delle materie del mattino seguente.
<i>"Non ricordarmi le materie"</i> - Smetterò di ricordarti delle tue materie.
<i>"Mostrami i compleanni salvati"</i> - Per vedere l'elenco dei compleanni salvati.
<i>"Aggiungi i compleanni della 3BS"</i> - Aggiungerò i compleanni della 3BS ai tuoi compleanni salvati.

<b>Comandi vocali e testuali:</b>
<i>"Nome Cognome compie gli anni il DD/MM"</i> - Per aggiungere un compleanno.
<i>"Dimentica il compleanno di Nome Cognome"</i> - Per eliminare un compleanno.
<i>"Quando compie gli anni Nome Cognome?"</i> - Per sapere quando qualcuno compie gli anni.
<i>"Quando c'è lezione di _____?"</i> - Per sapere la prossima volta che c'è una materia.
<i>"Come stai?"</i> - Per sapere come sto.
<i>"Che ore sono?"</i> - Per sapere che ore sono.

Se mi invii un file di testo ti invierò un vocale dove lo leggo ad alta voce.
"""
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
    )


def help_command(update: Update, context: CallbackContext):
    """Sends the user a list of commands with their functions,
    as well as info on how to contact the developers."""
    text = (
        "Stai riscontrando un problema con il bot? Puoi contattare gli sviluppatori!"
        "\n • @gino_pincopallo \n • @Mattiiiaaa"
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

    text = context.user_data["recognized text"]

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
        text = "Non ho capito bene, ripeti perfavore."
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    transcribed_message = context.user_data["recognized_text"].lower()
    if "trascrivi" in transcribed_message:
        speech_to_text_file(update, context)
    elif "come stai" in transcribed_message:
        status_handler(update, context)
    elif "che ore sono" in transcribed_message:
        send_time(update, context)
    elif "quando c'è" in transcribed_message:
        send_next_lesson(update, context)
    elif "quando compie gli anni" in transcribed_message:
        send_specific_birthday(update, context)
    elif "compie gli anni" in transcribed_message:
        add_birthday(update, context, from_audio=True)
    elif "compleanno" in transcribed_message:
        send_specific_birthday(update, context)
    elif "dimentica" in transcribed_message:
        remove_birthday(update, context, from_audio=True)
    elif "mostrami i compleanni salvati" in transcribed_message:
        show_birthday_list(update, context)
    elif "ricordami dei compleanni salvati" in transcribed_message:
        remind_birthdays(update, context)
    elif "ricordami le materie" in transcribed_message:
        remind_schedule(update, context)
    elif "non ricordarmi dei compleanni salvati" in transcribed_message:
        stop_reminding_birthdays(update, context)
    elif "non ricordarmi le materie" in transcribed_message:
        stop_reminding_schedule(update, context)
    elif "aggiungi i compleanni della terza b s" in transcribed_message:
        add_known_birthdays(update, context)
    else:
        text = "Temo di non aver capito, puoi ripetere perfavore?"
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
    job_queue.run_daily(
        callback=send_schedule, days=(0, 1, 2, 3, 4, 5), time=time(hour=15)
    )
    job_queue.run_daily(callback=check_birthdays, time=time(hour=7))
    dispatcher.add_handler(CommandHandler("inizia", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("ricordami_compleanni", remind_birthdays))
    dispatcher.add_handler(CommandHandler("aggiungi_compleanni_3BS", add_known_birthdays))
    dispatcher.add_handler(CommandHandler("non_mi_ricordare_compleanni", stop_reminding_birthdays))
    dispatcher.add_handler(CommandHandler("ricordami_materie", remind_schedule))
    dispatcher.add_handler(CommandHandler("non_mi_ricordare_materie", stop_reminding_schedule))
    dispatcher.add_handler(CommandHandler("lista_comandi", send_command_list))
    dispatcher.add_handler(CommandHandler("compleanni_salvati", show_birthday_list))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"[Dd]imentica il compleanno di"), remove_birthday)
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
    dispatcher.add_handler(MessageHandler(Filters.regex(r"[Cc]he ore sono"), send_time))
    dispatcher.add_handler(MessageHandler(Filters.text, unrecognized_message_handler))
    
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
