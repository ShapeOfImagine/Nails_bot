from telebot import types
from static_data import bot, visiting_time, session
from services import TimeOperations, DatabaseOperations,create_datetime


def transfer_select_time(message):
    visiting_time.clear()
    visiting_time["day"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    time_points = TimeOperations.create_visiting_time()
    for point in time_points:
        markup.add(str(point))
    bot.send_message(message.from_user.id,
                     text=f"Ви вибрали дату {message.text} На який час вас записати?",
                     reply_markup=markup)
    bot.register_next_step_handler(message, transfer_event_set_time)


def transfer_event_set_time(message):
    visiting_time["hour"] = message.text
    new_time = create_datetime(visiting_time)
    order = DatabaseOperations.get_user_procedure(session, message.from_user.id)
    TimeOperations.change_order_time(order=order, meeting_time=new_time)
    bot.send_message(message.from_user.id,
                     text="Запис успішно перенесено",
                     reply_markup=types.ReplyKeyboardRemove())
