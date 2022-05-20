from datetime import datetime
from components.const import weekly_schedule, days_of_the_week
from telegram import Update
from telegram.ext import CallbackContext


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
            if (
                requested_subject == subject and weekday >= current_weekday):
                if len(class_time) > 5:
                    text = (
                        f"La prossima lezione di {subject} è {days_of_the_week[weekday]}"
                        f" dalle {class_time[:5]} alle {class_time[6:]}"
                    )
                else:
                    text = f"La prossima lezione di {subject} è {days_of_the_week[weekday]} alle {class_time}"
                return

            elif requested_subject == subject.replace("_", " ") and weekday < current_weekday:
                if len(class_time) > 5:
                    text = (
                        f"La prossima lezione di {subject} è {days_of_the_week[weekday]} di settimana prossima,"
                        f" dalle {class_time[:5]} alle {class_time[6:]}"
                    )
                else:
                    text = f"La prossima lezione di {subject} è {days_of_the_week[weekday]} di settimana prossima, alle {class_time}"
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                return

    text = f"Non ho trovato {requested_subject} tra le materie registrate"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def remind_schedule(update: Update, context: CallbackContext):
    """Starts reminding the user about his schedule."""

    chat_id = update.effective_chat.id
    if not context.bot_data.get(chat_id):
        context.bot_data[chat_id] = {}

    if context.bot_data[chat_id].get("Schedule"):
        text = "Lo stavo già facendo, ora puoi esserne doppiamente certo."
    else:
        text = "Ok! Da ora in poi ti ricorderò ogni giorno alle 15 le materie del giorno dopo."
        context.bot_data[chat_id]["Schedule"] = True
    context.bot.send_message(chat_id=chat_id, text=text)


def check_subjects(context: CallbackContext):
    """Checks if there are any subjects scheduled for the following day and sends them
    to all the users who subscribed."""

    weekday = datetime.now().weekday()
    if weekday == 6:
        return

    text = f"Ecco le materie di domani:\n{weekly_schedule[weekday]}"
    for user in context.bot_data:
        context.bot.send_message(chat_id=user, text=text)