from datetime import datetime, time
from components.const import known_birthdays
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext


def add_birthday(update: Update, context: CallbackContext, **kwargs):
    """Saves the new birthday to the user's birthday dictionary in bot_data."""

    try:
        user_message = update.message.text.split()
    except AttributeError:
        user_message = context.user_data["recognized_text"].split()

    try:
        name = user_message[0]
        surname = user_message[1]
        if kwargs.get("from_audio"):
            birthday = f"{user_message[6]} {user_message[7]}"
            birthday = time.strptime(birthday, "%d %B").strftime("%d/%m")
        else:
            birthday = user_message[6]
    except (ValueError, IndexError):
        text = (
            "Non credo di aver capito bene, potresti ripetere? Per aggiungere un compleanno "
            'devi dirmi: "Nome Cognome compie gli anni il DD/MM"'
        )

    chat_id = update.effective_chat.id
    context.bot_data[chat_id]["Birthdays"].update({f"{name} {surname}": birthday})

    text = f"Ok! Il {birthday} ti ricorderò del compleanno di {name} {surname}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remove_birthday(update: Update, context: CallbackContext, **kwargs):
    """Removes the birthday from the user's birthday dictionary in bot_data """
    try:
        user_message = update.message.text.split()
    except AttributeError:
        user_message = context.user_data["recognized_text"].split()

    try:
        name = user_message[0]
        surname = user_message[1]
        if kwargs.get("from_audio"):
            birthday = f"{user_message[6]} {user_message[7]}"
            birthday = time.strptime(birthday, "%d %B").strftime("%d/%m")
        else:
            birthday = user_message[6]
    except (ValueError, IndexError):
        text = (
            "Non credo di aver capito bene, potresti ripetere? Per aggiungere un compleanno "
            'devi dirmi: "Nome Cognome compie gli anni il DD/MM"'
        )

    chat_id = update.effective_chat.id
    context.bot_data[chat_id]["Birthdays"].update({f"{name} {surname}": birthday})

    text = f"Ok! Il {birthday} ti ricorderò del compleanno di {name} {surname}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def send_specific_birthday(update: Update, context: CallbackContext):
    """Sends the user the birthday of the chosen person."""

    try:
        user_message = update.message.text.split()
    except AttributeError:
        user_message = context.user_data["recognized_text"].split()

    name = f"{user_message[4]} {user_message[5]}".title()

    birthday = context.bot_data[update.effective_chat.id]["Birthdays"][name]
    birthday = datetime.strptime(birthday, "%d/%m").strftime("%#d %B")

    text = f"{name} compie gli anni il {birthday}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remind_birthdays(update: Update, context: CallbackContext):
    """Starts reminding the user about birthdays."""

    chat_id = update.effective_chat.id
    if not context.bot_data.get(chat_id):
        context.bot_data[chat_id] = {}
    if context.bot_data[chat_id].get("Birthdays"):
        text = "Lo stavo già facendo, ora puoi esserne doppiamente certo."
    else:
        text = (
            "Al momento non ho alcun compleanno di cui ricordarti. Vuoi aggiungerne qualcuno?"
            "\nSe vuoi, posso ricordarti dei compleanni della classe 3BS, quelli li so a memoria."
        )
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Ricordami dei compleanni della 3BS",
                        callback_data="add known birthdays",
                    )
                ]
            ]
        )

        context.bot_data[update.effective_chat.id]["Birthdays"] = {}

    context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def add_known_birthdays(update: Update, context: CallbackContext):
    """Adds known birthdays to user's birthdays"""

    chat_id = update.effective_chat.id
    context.bot_data[chat_id]["Birthdays"].update(known_birthdays)
    text = "Aggiunti ;)"
    context.bot.send_message(chat_id=chat_id, text=text)
