from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from components.const import known_birthdays
from components.utils import time_delta


def save_user(update: Update, context: CallbackContext):
    """Adds a dictionary to context.bot_data to save the new user's data in."""
    chat_id = update.effective_chat.id
    if context.bot_data.get(chat_id):
        if context.bot_data[chat_id].get("Birthdays"):
            return

    context.bot_data[chat_id] = {"Birthdays": {}, "remind birthdays": False}


def add_birthday(update: Update, context: CallbackContext, **kwargs):
    """Saves the new birthday to the user's birthday dictionary in bot_data."""
    save_user(update, context)

    try:
        user_message = update.message.text.split()
    except AttributeError:
        user_message = context.user_data["recognized_text"].split()

    try:
        name = user_message[0].title()
        surname = user_message[1].title()
        if kwargs.get("from_audio"):
            birthday = f"{user_message[6]} {user_message[7]}"
            birthday = datetime.strptime(birthday, "%d %B").strftime("%d/%m")
        else:
            birthday = user_message[6]
    except (ValueError, IndexError):
        text = (
            "Non credo di aver capito bene, potresti ripetere? Per aggiungere un compleanno "
            'dovresti dirmi: "Nome Cognome compie gli anni il DD/MM".'
        )

    chat_id = update.effective_chat.id
    reformatted_birthday = datetime.strptime(birthday, "%d/%m").strftime("%#d %B")
    if f"{name} {surname}" not in context.bot_data[chat_id]["Birthdays"]:
        text = f"Ok! Il {reformatted_birthday} ti ricorderò del compleanno di {name} {surname}."
    elif birthday not in context.bot_data[chat_id]["Birthdays"].values():
        text = (
            f"Ok! Ho modificato la data del suo compleanno al {reformatted_birthday}."
        )
    else:
        text = "Già me lo avevi detto."
        
    context.bot_data[chat_id]["Birthdays"].update({f"{name} {surname}": birthday})
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remove_birthday(update: Update, context: CallbackContext):
    """Removes the birthday from the user's birthday dictionary in bot_data"""
    save_user(update, context)

    try:
        user_message = update.message.text.split()
    except AttributeError:
        user_message = context.user_data["recognized_text"].split()

    try:
        name = user_message[4].title()
        surname = user_message[5].title()
    except IndexError:
        text = (
            "Non credo di aver capito bene, potresti ripetere? Per rimuovere un compleanno "
            'dovresti dirmi: "Dimentica il compleanno di Nome Cognome".'
        )

    chat_id = update.effective_chat.id
    try:
        context.bot_data[chat_id]["Birthdays"].pop(f"{name} {surname}")
        text = f"Ok! non ti ricorderò più del compleanno di {name} {surname}."
    except KeyError:
        text = (
            f"Non ho trovato il compleanno di {name} {surname} tra quelli salvati. Se vuoi "
            "verificare quali sono i compleanni salvati puoi usare il comando /compleanni_salvati."
        )

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def send_specific_birthday(update: Update, context: CallbackContext):
    """Sends the user the birthday of the chosen person."""
    try:
        user_message = update.message.text.split()
    except AttributeError:
        user_message = context.user_data["recognized_text"].split()

    name = f"{user_message[4]} {user_message[5]}".title().replace("?", "")
    try:
        birthday = context.bot_data[update.effective_chat.id]["Birthdays"][name]
        birthday = datetime.strptime(birthday, "%d/%m").strftime("%#d %B")
        text = f"{name} compie gli anni il {birthday}."
    except KeyError:
        text = (
            f"Non ho trovato il compleanno di {name} tra quelli salvati."
            " Usa /compleanni_salvati per vedere tutti i compleanni che hai salvato."
        )

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remind_birthdays(update: Update, context: CallbackContext):
    """Starts reminding the user about birthdays."""
    save_user(update, context)

    chat_id = update.effective_chat.id
    reply_markup = []
    if context.bot_data[chat_id]["remind birthdays"]:
        text = "Lo stavo già facendo, ora puoi esserne doppiamente certo."
    else:
        text = (
            "Al momento non ho alcun compleanno di cui ricordarti."
            "\nSe vuoi, posso ricordarti dei compleanni della classe 3BS, quelli li so a memoria.\n"
            "Se invece vuoi aggiungerne altri vedi come fare nella /lista_comandi."
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
    save_user(update, context)
    chat_id = update.effective_chat.id
    context.bot_data[chat_id]["remind birthdays"] = False
    context.bot.send_message(
        chat_id=chat_id, text="Ok! Non ti invierò più notifiche per i compleanni."
    )


def add_known_birthdays(update: Update, context: CallbackContext):
    """Adds known birthdays to user's birthdays"""
    chat_id = update.effective_chat.id
    context.bot_data[chat_id]["Birthdays"].update(known_birthdays)
    text = "Aggiunti ;)"
    context.bot.send_message(chat_id=chat_id, text=text)


def show_birthday_list(update: Update, context: CallbackContext):
    """Shows list of birthdays"""
    save_user(update, context)
    chat_id = update.effective_chat.id
    birthdays = context.bot_data[chat_id]["Birthdays"]
    if len(birthdays) != 0:
        text = "Ecco i compleanni che hai salvato:"
        sorted_dates = sorted(birthdays.items(), key=time_delta)
        for name, date in sorted_dates:
            text += f"\n{name}: {date}"
    else:
        text = (
            "Non hai salvato alcun compleanno al momento."
            " Puoi vedere come aggiungerne uno nella /lista_comandi"
        )
    context.bot.send_message(chat_id=chat_id, text=text)


def check_birthdays(context: CallbackContext):
    """Checks if the current date corresponds to any birthday saved by a user."""
    today = datetime.now().date().strftime("%d/%m")
    for user in context.bot_data:
        if user["remind birthdays"]:
            for name, birthday in user["Birthdays"].items():
                if birthday == today:
                    text = f"Oggi è il compleanno di {name}, fagli gli auguri!"
                    context.bot.send_message(chat_id=user, text=text)
        else:
            continue


if __name__ == "__main__":
    print("Questo file non dovrebbe essere eseguito.")
