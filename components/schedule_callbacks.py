from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext

from components.const import days_of_the_week, weekly_schedule


def send_next_lesson(update: Update, context: CallbackContext):
    """Sends the user a message containing info on when the next requested lesson is."""

    try:
        requested_subject = update.message.text[11:].lower().strip()
    except AttributeError:
        requested_subject = context.user_data["recognized_text"][11:].lower().strip()

    requested_subject = requested_subject.replace("?", "")
    for weekday, schedule in weekly_schedule.items():
        current_weekday = datetime.now().weekday()
        for hour in schedule:
            class_time, subject = hour.split()
            subject = subject.replace("_", " ")
            if requested_subject == subject and weekday >= current_weekday:
                if len(class_time) > 5:
                    text = (
                        f"La prossima lezione di {subject} è {days_of_the_week[weekday]}"
                        f" dalle {class_time[:5]} alle {class_time[6:]}."
                    )
                else:
                    text = (
                        f"La prossima lezione di {subject} è {days_of_the_week[weekday]}"
                        f" alle {class_time}."
                    )
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                return

            if (
                requested_subject == subject.replace("_", " ")
                and weekday < current_weekday
            ):
                if len(class_time) > 5:
                    text = (
                        f"La prossima lezione di {subject} è {days_of_the_week[weekday]}"
                        f" di settimana prossima, dalle {class_time[:5]} alle {class_time[6:]}."
                    )
                else:
                    text = (
                        f"La prossima lezione di {subject} è {days_of_the_week[weekday]}"
                        f" di settimana prossima, alle {class_time}."
                    )
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                return

    text = f"Non ho trovato {requested_subject} tra le materie registrate"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remind_schedule(update: Update, context: CallbackContext):
    """Starts reminding the user about his schedule."""
    chat_id = update.effective_chat.id
    if not context.bot_data.get(chat_id):
        context.bot_data[chat_id] = {}

    user_data = context.bot_data[chat_id]
    if user_data.get("remind schedule"):
        if user_data["remind schedule"]:
            text = "Ok! Sappi che lo stavo già facendo."
        else:
            text = "Ok! D'ora in poi ti ricorderò ogni giorno alle 15 delle materie del giorno dopo."
            context.bot_data[chat_id]["remind schedule"] = True
    else:
        text = "Ok! D'ora in poi ti ricorderò ogni giorno alle 15 delle materie del giorno dopo."
        context.bot_data[chat_id]["remind schedule"] = True
    context.bot.send_message(chat_id=chat_id, text=text)


def stop_reminding_schedule(update: Update, context: CallbackContext):
    """Stops reminding the user about his schedule."""
    chat_id = update.effective_chat.id
    if not context.bot_data.get(chat_id):
        context.bot_data[chat_id] = {}
    
    user_data = context.bot_data[chat_id]
    if user_data.get("remind schedule"):
        if user_data["remind schedule"]:
            text = "Ok! Non ti ricorderò più delle tue materie."
            context.bot_data[chat_id]["remind schedule"] = False
        else:
            text = "Ok! Tanto non lo stavo facendo comunque."
    else:
        text = "Ok! Tanto non lo stavo facendo comunque."
        
    context.bot.send_message(chat_id=chat_id, text=text)

def send_schedule(context: CallbackContext):
    """Checks if there are any subjects scheduled for the following day and sends them
    to all the users who subscribed."""
    weekday = datetime.now().weekday()
    text = "Ecco le materie di domani:"
    for subject in weekly_schedule[weekday]:
        text += f"\n- {subject}".replace("_", " ")

    for user in context.bot_data:
        context.bot.send_message(chat_id=user, text=text)


if __name__ == "__main__":
    print("Questo file non dovrebbe essere eseguito.")