from telebot import types
from configs import ADMIN_ID
from static_data import bot, session, calendar
from add_event import Add_event
from services import DatabaseOperations


class Admin_Services:
    """Admin user options block"""
    @staticmethod
    def admin_start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        bot.send_message(ADMIN_ID, text=f"Привет {message.from_user.first_name}")

        add_event = types.KeyboardButton("Додати запис")
        check_events = types.KeyboardButton("Показати активні записи")
        remove_event = types.KeyboardButton("Видалити запис")
        check_today = types.KeyboardButton("Хто в мене на сьогодні")
        check_tomorrow = types.KeyboardButton("Хто в мене на завтра")

        markup.add(add_event, check_events, remove_event, check_today, check_tomorrow)
        bot.send_message(ADMIN_ID, text="Чим можу допомогти?", reply_markup=markup)
        bot.register_next_step_handler(message, Admin_Services.admin_services_tree)

    @staticmethod
    def admin_services_tree(message):
        if message.text == "Додати запис":
            start_create_event(message)
        elif message.text == "Показати активні записи":

            events = DatabaseOperations.get_all_events(session)[0]
            for event in events:
                date = f"{event['date'].day}.{calendar[str(event['date'].month)]} " \
                       f"{event['date'].hour}:{event['date'].minute}"

                order = f"{event['user_first_name']} " \
                        f" {date}\n {event['procedure1']} " \
                        f"{event['procedure2']}"
                bot.send_message(ADMIN_ID, order)

        elif message.text == "Видалити запис":
            Admin_Services.admin_delete(message)

        elif message.text == "Хто в мене на сьогодні":
            pass
        elif message.text == "Хто в мене на завтра":
            pass

    @staticmethod
    def admin_delete(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        events = DatabaseOperations.get_all_events(session)[0]
        for event in events:
            date = f"{event['date'].day}.{calendar[str(event['date'].month)]}"
            order = f"id:{event['user_id']} {event['user_first_name']} {date}\n {event['procedure1']}"
            markup.add(order)
        bot.send_message(ADMIN_ID, text="Який саме запис видалити?", reply_markup=markup)
        bot.register_next_step_handler(message, DatabaseOperations.rem_selected_order)

    """End admin user options block"""


def start_create_event(message):
    """START OF CREATING ORDER"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    order = DatabaseOperations.get_user_procedure(session, message.from_user.id)
    if message.from_user.id != int(ADMIN_ID):
        if order:
            order_message = f"{order.meeting_time.strftime('%d.%m.%y %H:%M')} \n" \
                            f" Процедура: {order.procedure1} \n" \
                            f" Додаткові послуги: {order.procedure2}"
            bot.send_message(message.from_user.id, order_message)
            cancel_order = types.KeyboardButton("Скасувати запис")
            check_me_replace = types.KeyboardButton("Перенести запис")
            change_order = types.KeyboardButton("Змінити запис")
            markup.add(cancel_order, check_me_replace, change_order)
            bot.send_message(message.from_user.id,
                             text="Вибачете але у вас вже є активний запис \n"
                                  "Ви можете змінити час або видалити і створити новий запис",
                             reply_markup=markup)
        else:
            bot.register_next_step_handler(message, Add_event.wich_day)
    else:
        print("here")
        Add_event.wich_day(message)