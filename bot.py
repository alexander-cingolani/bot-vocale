from os import environ
from time import strftime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, datetime
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    CallbackQueryHandler,
    Updater,
    JobQueue,
)

from bot_utils import speech_to_text
import set_environment_vars
from bot_data import materie, day_of_week

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
def status_handler(update: Update, context: CallbackContext):
    text = "Sono un bot, non ho sensazioni. E tu?"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
def answer_handler(update: Update, context: CallbackContext):
    user_message = update.message.text
    if "bene" in user_message.lower():
        text = ":)"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    if "male" in user_message.lower():
        text = ":("
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        
def give_time_handler(update: Update, context: CallbackContext):
    time = f"sono le: {datetime.now().strftime('%h:m')}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=time)

def lezione_handler(update: Update, context: CallbackContext):
    user_message = update.message.text.split()
    for key,value in materie.items():
        value = value.split("•")
        for subject in value:
            if user_message[2] in subject:
                time,subject = subject.split()
                return f"{day_of_week[key]} alle {time} "
        
    
    
def add_birthday(update: Update, context: CallbackContext):
    file = open("compleanni.csv","a")
    user_message = update.message.text.split()
    file.write(f"{user_message[2]} {user_message[3]},{user_message[4]}\n")
    
    

def confirm_handler(update: Update, context: CallbackContext):
    """Asks user to confirm that the text generated from the voice message is correct."""

    if update.callback_query.data == "incorrect":
        text = "Non ho capito bene, ripeti perfavore."
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    text = "Strano, di solito non capisco una mazza."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    user_message = context.user_data["recognized_text"]
    if user_message == "come stai?":
        status_handler(update, context)
    elif user_message == "che ore sono?":
        give_time_handler(update, context)
    elif "quando c'è" in user_message.lower():
        lezione_handler(update, context)
    elif "aggiungi compleanno" in user_message:
        add_birthday(update,context)
    elif user_message[:13] == "compleanno di":
        "ciao"
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
    dispatcher.add_handler(MessageHandler(Filters.regex("bene|male|benissimo|uno schifo"),answer_handler ))
    dispatcher.add_handler(
        MessageHandler(Filters.text(""), unrecognized_message_handler)
    )

    updater.start_polling()


if __name__ == "__main__":
    main()
