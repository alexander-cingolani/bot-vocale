from os import environ
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    CallbackQueryHandler,
    Updater,
    JobQueue
)

from bot_utils import speech_to_text
import set_environment_vars

TOKEN = environ.get("TOKEN")
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


def start_command(update: Update, context: CallbackContext):
    """Welcomes the user and asks to send a voice message/command"""

    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Ciao! Al momento non faccio niente."
    )


def help_command(update: Update, context: CallbackContext):
    """Sends the user a list of commands and their functions
    as well as info on how to contact the developers."""

    text = (
        "Ecco una lista dei comandi che puoi utilizzare: "
        "******************************** DA RIEMPIRE **************************************"
        "Se stai riscontrando un problema con il bot, puoi contattare gli sviluppatori 💻"
        "\n• @gino_pincopallo\n• @id_telegram_mattia"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def audio_message_handler(update: Update, context: CallbackContext):
    """Handles any voice message received by the bot. After analizing its content
    it calls the appropriate function to reply to the user."""

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="TYPING")
    
    file_name = update.message.voice.get_file().download()
    context.user_data["recognized_text"] = speech_to_text(file_name)

    recognized_text = context.user_data["recognized_text"]
    text = f'Questo è quello che ho capito:\n"{recognized_text}"\nè corretto?'

    reply_markup = [
            [InlineKeyboardButton("Sì", callback_data="correct")],
            [InlineKeyboardButton("No", callback_data="incorrect")],
        ]

    context.user_data["message"] = context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, reply_markup=InlineKeyboardMarkup(reply_markup)
    )


def confirm_handler(update: Update, context: CallbackContext):
    """Asks user to confirm that the text generated from the voice message is correct."""

    if update.callback_query.data == "incorrect":
        text = "Non ho capito bene, ripeti perfavore."
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    text = "Strano, di solito non capisco una mazza."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    user_message = context.user_data["recognized_text"]
    if user_message == "lezione":
        pass
    elif user_message == "y":
        pass
    else:
        text = "Boh avevi detto che avevo capito bene ma non mi pare proprio, ripeti grazie"


def unrecognized_message_handler(update: Update, context: CallbackContext):
    """Handles any message which wasn't caught by the other handlers."""

    text = "n'agg capit"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def main():
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.voice, audio_message_handler))
    dispatcher.add_handler(CallbackQueryHandler(confirm_handler, pattern="correct|incorrect"))
    
    dispatcher.add_handler(
        MessageHandler(Filters.text(""), unrecognized_message_handler)
    )

    updater.start_polling()


if __name__ == "__main__":
    main()
