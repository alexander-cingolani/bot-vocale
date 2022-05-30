from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from components.const import known_birthdays
from components.utils import time_delta


def add_user(update: Update, context: CallbackContext):
    """Creates a new user profile if not already present."""

    chat_id = update.effective_chat.id
    if context.bot_data.get(chat_id):
        if context.bot_data[chat_id].get("Birthdays"):
            return

    context.bot_data[chat_id] = {"Birthdays": {}, "remind birthdays": False}


def get_message(update: Update, context: CallbackContext):
    """Returns the message sent by the user"""

    try:
        return update.message.text.lower()
    except AttributeError:
        return context.user_data["recognized_text"].lower()


def add_birthday(update: Update, context: CallbackContext):
    """Saves the new birthday to the user's birthday dictionary in bot_data."""
    
    add_user(update, context) # Adds user if not already registered
    user_message = get_message(update, context).replace("compie gli anni il ", "")
    # Accepts both date formats (DD/MM, DD Month)
    if "/" not in user_message:
        user_message = user_message.split()
        # If "/" is not in the message, the date will be the last two words.
        birthday = " ".join(user_message[-2:])
        name = " ".join(user_message[:-2]).title()
        birthday = datetime.strptime(birthday, "%d %B").strftime("%d/%m") 
    elif "/" in user_message:
        user_message = user_message.split()
        # If "/" is in the message, the date will be the last word
        birthday = user_message[-1] 
        name = " ".join(user_message[:-1]).title()
    else:
        text = (
            "Non ho capito, puoi ripetere? Per aggiungere un compleanno "
            'dovresti dirmi: "Nome Cognome compie gli anni il DD/MM".'
        )
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    chat_id = update.effective_chat.id
    reformatted_birthday = datetime.strptime(birthday, "%d/%m").strftime("%#d %B")
    if name not in context.bot_data[chat_id]["Birthdays"]:
        text = f"Ok! Il {reformatted_birthday} ti ricorderò del compleanno di {name}."
    elif birthday not in context.bot_data[chat_id]["Birthdays"].values():
        text = f"Ok! Ho modificato la data del suo compleanno al {reformatted_birthday}."
    else:
        text = "Me lo avevi già detto."
    context.bot_data[chat_id]["Birthdays"].update({name: birthday}) # Save birthday
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remove_birthday(update: Update, context: CallbackContext):
    """Removes the birthday from the user's birthday dictionary in bot_data"""

    add_user(update, context)
    name = get_message(update, context).replace("dimentica il compleanno di ", "").title()
    chat_id = update.effective_chat.id
    try:
        context.bot_data[chat_id]["Birthdays"].pop(name)
        text = f"Ok! non ti ricorderò più del compleanno di {name}."
    except KeyError:
        text = (
            f"Non ho trovato il compleanno di {name} tra quelli salvati. Se vuoi "
            "verificare quali sono i compleanni salvati puoi usare il comando /compleanni_salvati."
        )
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def delete_all_birthdays(update: Update, context: CallbackContext):
    """Deletes all saved birthdays."""

    add_user(update, context)
    context.bot_data[update.effective_chat.id]["Birthdays"].clear()
    text = "Fatto. Ho eliminato tutti i compleanni salvati."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def send_specific_birthday(update: Update, context: CallbackContext):
    """Sends the user the birthday of the chosen person."""
    
    add_user(update, context)
    name = get_message(update, context).replace("quando compie gli anni ", "").replace("?", "").title()
    try:
        birthday = context.bot_data[update.effective_chat.id]["Birthdays"][name]
        birthday = datetime.strptime(birthday, "%d/%m").strftime("%#d %B")
        text = f"{name} compie gli anni il {birthday}."
    except KeyError:
        text = (
            f"Non ho trovato il compleanno di {name} tra quelli salvati."
            " Usa /compleanni_salvati per vedere i compleanni che salvati."
        )

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remind_birthdays(update: Update, context: CallbackContext):
    """Starts reminding the user about birthdays."""

    add_user(update, context)
    chat_id = update.effective_chat.id
    reply_markup = []
    if context.bot_data[chat_id]["remind birthdays"]:
        text = "Lo stavo già facendo, ora puoi esserne doppiamente certo."
    else:
        text = (
            "Al momento non ho alcun compleanno di cui ricordarti."
            "\nSe vuoi, posso ricordarti dei compleanni della classe 3BS.\n"
            "Se invece ne vuoi aggiungere altri vedi come fare nella /lista_comandi."
        )
        reply_markup = [
            InlineKeyboardButton(
                "Ricordami dei compleanni della 3BS",
                callback_data="add known birthdays",
            )
        ]
        context.bot_data[chat_id]["remind birthdays"] = True

    context.bot.send_message(
        chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup([reply_markup])
    )


def stop_reminding_birthdays(update: Update, context: CallbackContext):
    """Stops reminding the user about birthdays"""

    add_user(update, context)
    chat_id = update.effective_chat.id
    context.bot_data[chat_id]["remind birthdays"] = False
    context.bot.send_message(
        chat_id=chat_id, text="Ok! Non ti invierò più notifiche per i compleanni."
    )


def add_known_birthdays(update: Update, context: CallbackContext):
    """Adds known birthdays to user's birthdays"""

    chat_id = update.effective_chat.id
    context.bot_data[chat_id]["Birthdays"].update(known_birthdays)
    text = "Aggiunti!\nPuoi consultarli tra i /compleanni_salvati"
    context.bot.send_message(chat_id=chat_id, text=text)


def show_birthday_list(update: Update, context: CallbackContext):
    """Shows a sorted list of the user's birthdays"""

    add_user(update, context)
    chat_id = update.effective_chat.id
    birthdays = context.bot_data[chat_id]["Birthdays"]
    if len(birthdays) != 0:
        text = "Ecco i compleanni che hai salvato:"
        sorted_dates = sorted(birthdays.items(), key=time_delta)
        for name, date in sorted_dates:
            text += f"\n{name}: {date}"
    else:
        text = (
            "Non hai alcun compleanno salvato al momento."
            " Puoi vedere come aggiungerne uno nella /lista_comandi"
        )
    context.bot.send_message(chat_id=chat_id, text=text)


def check_birthdays(context: CallbackContext):
    """Checks if the current date corresponds to any birthday saved by a user."""

    today = datetime.now().date().strftime("%d/%m")
    for user in context.bot_data:
        if user.get("remind birthdays"):
            for name, birthday in user["Birthdays"].items():
                if birthday == today:
                    text = f"Oggi è il compleanno di {name}, fagli gli auguri!"
                    context.bot.send_message(chat_id=user, text=text)


if __name__ == "__main__":
    print("Questo file non dovrebbe essere eseguito.")
