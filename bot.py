import time
import schedule
from telebot import types
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from add_event import Add_event
from static_data import session, bot, calendar, new_services
from configs import ADMIN_ID, INSTA_MESSAGE_PART, INSTA_LINK
from services import visiting_time, create_datetime,\
    DatabaseOperations, TimeOperations, ServiceOperations


admin_id = ADMIN_ID



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


@bot.message_handler(commands=["start"])
def start(message):
    clear_services()
    user = message.from_user
    first_name = user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    if message.from_user.id == int(ADMIN_ID):
        Admin_Services.admin_start(message)

    else:
        if DatabaseOperations.user_exist(session, message.from_user.id):
            # welcome letter if user already exist
            bot.send_message(message.from_user.id,
                             f"Рада знову вас бачити, {first_name} ! 🖐\n"
                             f"INSTA: {INSTA_MESSAGE_PART}{INSTA_LINK}",
                             parse_mode="markdown")

        else:
            # welcome letter if user not exist
            bot.send_message(message.from_user.id, f"Вітаю, {first_name} ! 🖐\n"
                                                   f"Я бот для запису до {INSTA_MESSAGE_PART}{INSTA_LINK}",
                                                   parse_mode="markdown")

        """CREATING START BUTTONS"""
        check_me_in = types.KeyboardButton("Записатися")
        check_me_time = types.KeyboardButton("Нагадати про запис")
        check_me_replace = types.KeyboardButton("Перенести запис")
        cancel_order = types.KeyboardButton("Скасувати запис")
        change_order =types.KeyboardButton("Змінити запис")
        markup.add(check_me_in, check_me_time, check_me_replace, cancel_order, change_order)

        bot.send_message(message.from_user.id,
                         text="Чим можу допомогти?",
                         reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Записатися")
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


@bot.message_handler(func=lambda message: message.text.lower() == "скасувати запис"
                     or message.text == "Видалити запис")
def cancel_event(message):
    if message.from_user.id == int(ADMIN_ID):
        Admin_Services.admin_delete(message)
        return
    """REMOVE ORDER IF EXISTS"""
    keyboard = InlineKeyboardMarkup()
    to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
    check_me_in = InlineKeyboardButton(text="Записатися", callback_data="create_order")
    keyboard.add(to_start, check_me_in)

    order = DatabaseOperations.get_user_procedure(session, message.from_user.id)
    if order:
        bot.send_message(message.from_user.id, f"{order.meeting_time.strftime('%d.%m.%y %H:%M')} "
                                               f"\n {order.procedure1}"
                                               f" \n {order.procedure2}")
        DatabaseOperations.remove_order_record(session, message.from_user.id)
        bot.send_message(message.from_user.id,
                         text="Ваш запис скасовано, Якщо бажаєте створити новий натисніть на кнопку 'Створити запис'",
                         reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id,
                         text="У вас не знайдено активних записів, Бажаєте створити?",
                         reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text.lower() == "перенести запис")
def transfer_event(message):
    """CHANGE ORDER TIME"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    order = DatabaseOperations.get_user_procedure(session, message.from_user.id)
    if order:
        Add_event.wich_day(message, common_stream=False)
        new_meeting_time = create_datetime(visiting_time)
        """Залишилось придумати як і куди передавати ордер обьект"""
        TimeOperations.change_order_time(order=order, meeting_time=new_meeting_time)
        bot.send_message(message.from_user.id,
                         text="Ваш запис перенесено",
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        # event by user id is not exists
        check_me_in = types.KeyboardButton("Записатися")
        markup.add(check_me_in)
        bot.send_message(message.from_user.id, text="У вас немає активного запису який можна перенести",
                         reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.lower() == "нагадати про запис")
def recall_event(message):
    order = DatabaseOperations.get_user_procedure(session, message.from_user.id)
    if order:
        bot.send_message(message.from_user.id,
                         text=f"Звісно, 🤗\n"
                              f"Ви записані на {TimeOperations.week[order.meeting_time.strftime('%A')]} "
                              f"{order.meeting_time.strftime('%d.%m %H:%M')}")
    else:
        # event by user id is not exists
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        check_me_in = types.KeyboardButton("Записатися")
        markup.add(check_me_in)
        bot.send_message(message.from_user.id,
                         text="Вибачте але у вас поки що немає активних записів",
                         reply_markup=markup)


def reminder():
    """"""
    today_event = TimeOperations.get_order_by_date(datetime.today())
    if today_event:
        time_difference = today_event["date"] - datetime.now()
        if timedelta(hours=1) > time_difference:
            print("Осталось менше часа к процедуре")
        else:
            print(time_difference)


def clear_services():
    """CLEAR TEMPORARY FOLDER AFTER OR BEFORE USERGE"""
    new_services["services"].clear()
    new_services["additions"].clear()


def final_message(chat_id):
    keyboard = InlineKeyboardMarkup()
    to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
    bot_order = InlineKeyboardButton(text="також хочу бот", callback_data="need_bot")
    keyboard.add(to_start, bot_order)
    bot.send_message(chat_id, text="Якщо ви підприємець і вас зацікавила можливість оптимізації свого бізнесу"
                                   " за допомогою аналогічного боту або іншого продукту"
                                   "натисніть (також хочу бот)", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Змінити запис")
def user_change_order(message):
    order = DatabaseOperations.get_user_procedure(session, message.from_user.id)

    if order:
        clear_services()
        order_info = ServiceOperations.create_order_info(order)
        DatabaseOperations.remove_order_record(session, order.user_id)
        order_message = f"  Ваше замовлення: {order_info['first_name']}\n" \
                        f"{', '.join(order_info['services'])}\n" \
                        f"Додаткові послуги: {', '.join(order_info['additions'])}\n" \
                        f"Ваш контактний номер:  {order_info['user_phone']}\n" \
                        f"Дата прийому: {TimeOperations.week[order_info['time'].strftime('%A')]}" \
                        f" {order_info['time'].strftime('%d.%m.%y %H:%M')}"
        bot.send_message(message.from_user.id,
                         text=order_message,
                         reply_markup=types.ReplyKeyboardRemove())
        order_time = order.meeting_time
        Add_event.kind_service(message, meeting_time=order_time)

    else:
        bot.send_message(message.from_user.id, text="У вас немає активних записів, \n"
                                                    "Ви можете вийти на головну і створити")
        # event by user id is not exists
        final_message(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "need_bot")
def bot_propose():
    pass


@bot.callback_query_handler(func=lambda call: call.data == "to_mainboard")
def check_button(call):
    bot.answer_callback_query(call.id, "На головну")
    start(call)


@bot.callback_query_handler(func=lambda call: call.data == "create_order")
def start_create_order_handler(call):
    bot.answer_callback_query(call.id, "створити запис")

    start_create_event(call.message)


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


def start_bot():
    while True:
        try:
            # Start polling
            bot.polling(none_stop=True, interval=0, timeout=30)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying in 3 seconds...")
            time.sleep(3)


if __name__ == "__main__":
    # reminder()
    schedule.every(1).hours.do(TimeOperations.rem_past_events)
    start_bot()
    while True:
        print("run autoremove old orders")
        schedule.run_pending()
        time.sleep(10)
