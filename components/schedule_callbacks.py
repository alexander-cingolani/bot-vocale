from datetime import datetime,timedelta

from telegram import Update
from telegram.ext import CallbackContext

from components.const import days_of_the_week, weekly_schedule


def add_user(update: Update, context: CallbackContext):
    """Adds a dictionary to context.bot_data to save the new user's data in."""
    
    chat_id = update.effective_chat.id
    if context.bot_data.get(chat_id):
        if context.bot_data[chat_id].get("remind schedule"):
            return
    context.bot_data[chat_id] = {"remind schedule": False}


def send_next_lesson(update: Update, context: CallbackContext):
    """Sends the user a message with date and time of the next lesson."""

    try:
        requested_subject = update.message.text[11:].lower()
    except AttributeError:
        requested_subject = context.user_data["recognized_text"][11:].lower()
    
    requested_subject = requested_subject.replace("?", "").replace(" ", "_")
    current_weekday = datetime.now().weekday()
    
    for weekday, schedule in weekly_schedule.items():
        if weekday > current_weekday and requested_subject in schedule:
            start, end = schedule[requested_subject].split("-")
            text = (
                    f"La prossima lezione di {requested_subject} è {days_of_the_week[weekday]}"
                    f" dalle {start} alle {end}."
                )
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return

    for weekday, schedule in weekly_schedule.items():
        if requested_subject in schedule:
            start, end = weekly_schedule[weekday][requested_subject].split("-")
            text = (
                    f"La prossima lezione di {requested_subject} è {days_of_the_week[weekday]}"
                    f" di settimana prossima dalle {start} alle {end}."
                    )
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return
    
    text = f"Non ho trovato {requested_subject} tra le materie salvate."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remind_schedule(update: Update, context: CallbackContext):
    """Starts reminding the user about his schedule."""

    chat_id = update.effective_chat.id
    add_user(update, context)
    user_data = context.bot_data[chat_id]
    if not user_data.get("remind schedule"):
        text = "Ok! Ogni giorno alle 15 ti ricorderò delle materie del giorno dopo."
        context.bot_data[chat_id]["remind schedule"] = True
    else:
        text = "Ok! Sappi che lo stavo già facendo."
    context.bot.send_message(chat_id=chat_id, text=text)


def stop_reminding_schedule(update: Update, context: CallbackContext):
    """Stops reminding the user about his schedule."""

    chat_id = update.effective_chat.id
    add_user(update, context)
    user_data = context.bot_data[chat_id]

    if not user_data.get("remind schedule"):
        text = "Ok! Tanto non lo stavo facendo comunque."
        context.bot.send_message(chat_id=chat_id, text=text)
        return

    text = "Ok! Non ti ricorderò più delle tue materie."
    context.bot_data[chat_id]["remind schedule"] = False
    context.bot.send_message(chat_id=chat_id, text=text)
    

def send_schedule(context: CallbackContext):
    """Sends each (subscribed) user the following day's schedule."""

    weekday = (datetime.now() + timedelta(days=1)).weekday()
    text = "Ecco le materie di domani:"
    for subject, hours in weekly_schedule[weekday].items():
        text += f"\n- {subject.replace('_', ' ')} ({hours})"

    for user in context.bot_data:
        if user.get("remind schedule"):
            context.bot.send_message(chat_id=user, text=text)


if __name__ == "__main__":
    print("Questo file non dovrebbe essere eseguito.")
