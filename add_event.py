import telebot

from configs import TOKEN
from telebot import types
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from models import User
from static_data import bot, session, new_services
from bot_calendar import transfer_event_set_time, transfer_select_time
from services import TimeOperations, DatabaseOperations, ServiceOperations, visiting_time,\
    get_estimated_time

from configs import ADDITIVES_LIST, ADMIN_ID


admin_id = ADMIN_ID


class Add_event:
    """Adding event methods block"""
    @staticmethod
    def wich_day(message):
        # select order day
        user_id = message.from_user.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        days_list = TimeOperations.get_free_dates()
        for day in days_list:
            markup.add(str(day))
        bot.send_message(user_id, text="На який день бажаєта записатись?", reply_markup=markup)

        bot.register_next_step_handler(message, Add_event.select_time)
        # else:
        #     print("false")
        #     bot.register_next_step_handler(message, transfer_select_time)

    @staticmethod
    def select_time(message, common_stream=True):
        # select event time
        visiting_time.clear()
        visiting_time["day"] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        time_points = TimeOperations.create_visiting_time()
        for point in time_points:
            markup.add(str(point))
        bot.send_message(message.from_user.id,
                         text=f"Ви вибрали дату {message.text} На який час вас записати?",
                         reply_markup=markup)
        if common_stream:
            bot.register_next_step_handler(message, Add_event.kind_service)
        else:
            transfer_event_set_time(message)

    @staticmethod
    def kind_service(message, meeting_time=False):
        if message.text.replace(":", "").isdigit():
            visiting_time["hour"] = message.text
        if meeting_time:
            visiting_time["hour"] = meeting_time.strftime("%H:%M")
            visiting_time["day"] = meeting_time.strftime("%d.%m.%y")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        # event by user id is not exists
        manikyr = types.KeyboardButton("Ручки 💅")
        pedik = types.KeyboardButton("Ніжки 👣")
        markup.add(manikyr, pedik)
        bot.send_message(message.from_user.id,
                         text="Оберіть процедуру",
                         reply_markup=markup)
        if meeting_time:
            # изменить на ветку без вибора времени
            bot.register_next_step_handler(message, Add_event.hands_or_foots_selection)
        else:
            bot.register_next_step_handler(message, Add_event.hands_or_foots_selection)


    @staticmethod
    def hands_or_foots_selection(message):
        """USER SELECTED KIND OF NAILS PROCEDURE"""
        new_services["kind_nails_procedure"] = message.text[:5]

        if message.text.lower() == "ручки 💅":
            Add_event.hands_services(message)
        elif message.text.lower() == "ніжки 👣":
            Add_event.foots_services(message)

    @staticmethod
    def hands_services(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        manik1 = types.KeyboardButton("Манікюр гігієнічний")
        manik2 = types.KeyboardButton("Манікюр з покриттям")
        manik3 = types.KeyboardButton("Манікюр з покр + укріплення")
        manik4 = types.KeyboardButton("Нарощення")
        markup.add(manik1, manik2, manik3, manik4)
        bot.send_message(message.from_user.id, text="Оберіть, що саме вас цікавить ⬇️", reply_markup=markup)
        bot.register_next_step_handler(message, Add_event.additions)

    @staticmethod
    def foots_services(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        pedik1 = types.KeyboardButton("Педикюр гігієнічний")
        pedik2 = types.KeyboardButton("Педикюр з покриттям")
        markup.add(pedik1, pedik2)
        bot.send_message(message.from_user.id, text="Оберіть, що саме вас цікавить ⬇️", reply_markup=markup)
        bot.register_next_step_handler(message, Add_event.kind_of_foot_service)

    @staticmethod
    def kind_of_foot_service(message):
        new_services["services"].append(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        if message.text.lower() == "педикюр гігієнічний" or message.text.lower() == "педикюр з покриттям":
            foots_gigiena1 = types.KeyboardButton("Тільки пальчики")
            foots_gigiena2 = types.KeyboardButton("Пальчики + стопа")
            markup.add(foots_gigiena1, foots_gigiena2)
        bot.send_message(message.from_user.id, text="Оберіть, що саме вас цікавить ⬇️", reply_markup=markup)
        bot.register_next_step_handler(message, Add_event.additions)

    @staticmethod
    def additions(message):
        new_services["services"].append(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        additions1 = types.KeyboardButton("Френч")
        additions2 = types.KeyboardButton("Слайдери")
        additions3 = types.KeyboardButton("Стемпінг")
        additions4 = types.KeyboardButton("Фольга")
        additions5 = types.KeyboardButton("Роспис")
        additions6 = types.KeyboardButton("Камінчики")
        additions7 = types.KeyboardButton("Не потребую")
        markup.add(additions1, additions2, additions3, additions4, additions5, additions6, additions7)
        bot.send_message(message.from_user.id, text="Оберіть додаткові послуги", reply_markup=markup)
        if len(new_services["services"]) + len(new_services["additions"]) < 4:
            bot.register_next_step_handler(message, Add_event.second_event_request)
        else:
            bot.register_next_step_handler(message, Add_event.wich_day)

    @staticmethod
    def second_event_request(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        new_services["additions"].append(message.text)
        if new_services["kind_nails_procedure"] == "Ручки":
            final_message1 = types.KeyboardButton("Хочу ще педикюр")
            final_message2 = types.KeyboardButton("Завершити запис")
            markup.add(final_message1, final_message2)
            bot.send_message(message.from_user.id, text="Бажаєте додати ще послуги?", reply_markup=markup)
            bot.register_next_step_handler(message, Add_event.second_event)

        elif new_services["kind_nails_procedure"] == "Ніжки":
            final_message1 = types.KeyboardButton("Хочу ще манікюр")
            final_message2 = types.KeyboardButton("Завершити запис")
            markup.add(final_message1, final_message2)
            bot.send_message(message.from_user.id, text="Бажаєте додати ще послуги?", reply_markup=markup)
            bot.register_next_step_handler(message, Add_event.second_event)

    @staticmethod
    def second_event(message):
        if message.text == "Хочу ще манікюр":
            Add_event.hands_services(message)
        elif message.text == "Хочу ще педикюр":
            Add_event.foots_services(message)
        else:
            Add_event.final(message)

    @staticmethod
    def final(message, meeting_time=False):
        """ADD EVENT TO DB IF USER ALREADY EXISTS"""
        if not meeting_time:
            print(visiting_time["day"], visiting_time["hour"])
        if message.text in ADDITIVES_LIST:
            new_services["additions"].append(message.text)
        new_services["user_first_name"] = message.from_user.first_name
        if not DatabaseOperations.user_exist(session, message.from_user.id):
            bot.send_message(message.from_user.id,
                             text="Вкажіть ваш номер мобільного для зворотнього зв'язку",
                             reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, Add_event.get_user_phone)
        else:
            bot.send_message(message.from_user.id,
                         text="________________________________",
                         reply_markup=types.ReplyKeyboardRemove())
            new_services["user_phone"] = DatabaseOperations.get_user_info(session, message.from_user.id).user_mobile
            Add_event.event_to_db(user_id=message.from_user.id, meeting_time=TimeOperations.get_visiting_datetime())


    @staticmethod
    def get_user_phone(message):
        try:
            phone = ServiceOperations.is_valid_phone(message.text)
            if phone:
                new_services["user_phone"] = phone
                """IF PHONE IS VALID ADD USER TO DATABASE"""
                user = User(user_id=message.from_user.id,
                            username=message.from_user.username,
                            first_name=message.from_user.first_name,
                            last_name=message.from_user.last_name,
                            mobile=new_services["user_phone"])
                DatabaseOperations.add_user(session, user)
                Add_event.event_to_db(user_id=message.from_user.id, meeting_time=datetime.utcnow())

            else:
                """IF PHONE IS NOT VALID TRY AGAIN"""
                bot.send_message(message.from_user.id, text="Ви вказали некоректний номер🤨, введіть будь ласка ще раз")
                bot.register_next_step_handler(message, Add_event.get_user_phone)

        except AttributeError as err:
            print("Error get phone", err)
            bot.send_message(message.from_user.id, text="Ви вказали некоректиний номер🤨, введіть будьласка ще раз")
            bot.register_next_step_handler(message, Add_event.get_user_phone)

    @staticmethod
    def event_to_db(user_id: int, meeting_time: datetime):
        time_price = get_estimated_time(new_services["services"])
        order_message = f"Ваше замовлення: {new_services['user_first_name']}\n"\
                        f"дата замовлення: " \
                        f"{TimeOperations.week[meeting_time.strftime('%A')]} " \
                        f"{meeting_time.strftime('%d.%m.%y %H:%M')}\n"\
                        f"{', '.join(new_services['services'])}\n" \
                        f"Додаткові послуги: {', '.join(new_services['additions'])}\n" \
                        f"Ваш контактний номер:  {new_services['user_phone']}\n" \
                        f"Орієнтовна ціна: {time_price['estim_price']}\n" \
                        f"Орієнтовна тривалість: {time_price['estim_time']} години"



        print(order_message)
        bot.send_message(admin_id, order_message)
        order = ServiceOperations.create_order(new_services=new_services, user_id=user_id, time=meeting_time)
        DatabaseOperations.add_procedure(session, order)
        bot.send_message(user_id, f"Ви успішно записались \n"
                                  f"{order_message}")
        clear_services()
        Add_event.final_message(user_id)

    @staticmethod
    def final_message(chat_id):
        keyboard = InlineKeyboardMarkup()
        to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
        bot_order = InlineKeyboardButton(text="також хочу бот", callback_data="need_bot")
        keyboard.add(to_start, bot_order)
        bot.send_message(chat_id, text="Якщо ви підприємець і вас зацікавила можливість оптимізації свого бізнесу"
                                        " за допомогою аналогічного боту або іншого продукту"
                                        "натисніть (також хочу бот)", reply_markup=keyboard)

        """And of Adding event methods block"""


def clear_services():
    """CLEAR TEMPORARY FOLDER AFTER OR BEFORE USERGE"""
    new_services["services"].clear()
    new_services["additions"].clear()
