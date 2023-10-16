from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from datetime import date, timedelta

from configs import ADMIN_ID
from static_data import bot, session, calendar
from addevent import AddEvent
from models import Order
from services import DatabaseOperations, ServiceOperations
from bot_calendar import CalendarHandlers


class AdminServices:
    """Admin user options block"""
    @staticmethod
    def admin_start(message):
        keyboard = InlineKeyboardMarkup()
        bot.send_message(ADMIN_ID, text=f"Привіт {message.from_user.first_name}")

        add_event = InlineKeyboardButton("Додати запис", callback_data="create_order")
        check_events = InlineKeyboardButton("Показати активні записи", callback_data="show_active_events")
        remove_event = InlineKeyboardButton("Видалити запис", callback_data="remove_event")
        check_today = InlineKeyboardButton("Хто в мене на сьогодні", callback_data="show_today_events")
        check_tomorrow = InlineKeyboardButton("Хто в мене на завтра", callback_data="show_tomorrow_events")
        shedule_settings = InlineKeyboardButton("Керування розкладом", callback_data="schedule_settings")

        keyboard.add(add_event, check_events, remove_event, check_today, check_tomorrow, shedule_settings)
        bot.send_message(ADMIN_ID, text="Чим можу допомогти?", reply_markup=keyboard)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == "show_active_events")
    def show_active_events(call):
        events = DatabaseOperations.get_all_events()[0]
        if events:
            for event in events:
                date = f"{event['date'].day}.{calendar[str(event['date'].month)]} " \
                       f"{event['date'].hour}:{event['date'].minute}"

                order = f"{event['user_first_name']} " \
                        f" {date}\n {event['procedure1']} " \
                        f"{event['procedure2']}"
                bot.send_message(ADMIN_ID, order, reply_markup=ReplyKeyboardRemove())
        else:
            keyboard = InlineKeyboardMarkup()
            to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
            add_event = InlineKeyboardButton("Додати запис", callback_data="create_order")
            keyboard.add(to_start, add_event)
            bot.send_message(ADMIN_ID,
                             text="Схоже що список записів наразі пустий",
                             reply_markup=keyboard)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == "remove_event")
    def admin_delete(call):
        message = ServiceOperations.callback_convert(call)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        events = DatabaseOperations.get_all_events()[0]
        for event in events:
            date = f"{event['date'].day}.{calendar[str(event['date'].month)]}"
            order = f"id:{event['user_id']} {event['user_first_name']} {date}\n {event['procedure1']}"
            markup.add(order)
        bot.send_message(ADMIN_ID, text="Який саме запис видалити?", reply_markup=markup)
        bot.register_next_step_handler(message, DatabaseOperations.rem_selected_order)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == "schedule_settings")
    def schedule_settings(call):
        keyboard = InlineKeyboardMarkup()
        default_week = InlineKeyboardButton("розклад днів тижня", callback_data="week_settings")
        current_week_settings = InlineKeyboardButton("розклад цього тижня", callback_data="current_week")
        next_week_settings = InlineKeyboardButton("розклад наступного тижня", callback_data="current_week")
        set_schedule_by_day = InlineKeyboardButton("розклад на вибраний день", callback_data="set_day")
        keyboard.add(default_week, current_week_settings, next_week_settings, set_schedule_by_day)
        bot.send_message(ADMIN_ID,
                         text="В цьому розділі ви можете планувати свій розклад",
                         reply_markup=keyboard)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == "week_settings")
    def poll_week_settings(call):
        CalendarHandlers.week_settings_sel_day(call)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == "show_today_events")
    def show_today_events(call):
        today = date.today()
        events = Order.get_orders_by_date(today)
        if events:
            for event in events:
                bot.send_message(ADMIN_ID, text=event)
            keyboard = InlineKeyboardMarkup()
            to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
            add_event = InlineKeyboardButton("Додати запис", callback_data="create_order")
            keyboard.add(to_start, add_event)
            bot.send_message(ADMIN_ID,
                             text="Можу ще чимось допомогти?",
                             reply_markup=keyboard)

        else:
            keyboard = InlineKeyboardMarkup()
            to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
            add_event = InlineKeyboardButton("Додати запис", callback_data="create_order")
            keyboard.add(to_start, add_event)
            bot.send_message(ADMIN_ID,
                             text="На сьогодні список записів пустий",
                             reply_markup=keyboard)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == "show_tomorrow_events")
    def show_tomorrow_events(call):
        tomorrow = date.today()
        tomorrow += timedelta(days=1)
        events = Order.get_orders_by_date(tomorrow)
        if events:
            for event in events:
                bot.send_message(ADMIN_ID, text=event)
            keyboard = InlineKeyboardMarkup()
            to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
            add_event = InlineKeyboardButton("Додати запис", callback_data="create_order")
            keyboard.add(to_start, add_event)
            bot.send_message(ADMIN_ID,
                             text="Можу ще чимось допомогти?",
                             reply_markup=keyboard)


        else:
            keyboard = InlineKeyboardMarkup()
            to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
            add_event = InlineKeyboardButton("Додати запис", callback_data="create_order")
            keyboard.add(to_start, add_event)
            bot.send_message(ADMIN_ID,
                             text="На завтра список записів пустий",
                             reply_markup=keyboard)

    """End admin user options block"""


def start_create_event(message):
    """START OF CREATING ORDER"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    order = Order.get_user_order(message.from_user.id)
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

            bot.register_next_step_handler(message, AddEvent.wich_day)
    else:
        print("here")
        AddEvent.wich_day(message)
