from telebot import types
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from models import User, Order
from static_data import bot, new_services, visiting_time, clear_services
from timeoperations import TimeOperations
from services import ServiceOperations


from configs import ADDITIVES_LIST, ADMIN_ID


admin_id = ADMIN_ID


class AddEvent:
    """Adding event methods block"""

    @staticmethod
    def kind_service(message):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        # event by user id is not exists
        manikyr = types.KeyboardButton("Ручки 💅")
        pedik = types.KeyboardButton("Ніжки 👣")
        markup.add(manikyr, pedik)
        bot.send_message(message.from_user.id,
                         text="Оберіть процедуру",
                         reply_markup=markup)

        bot.register_next_step_handler(message, AddEvent.hands_or_foots_selection)

    @staticmethod
    def hands_or_foots_selection(message):
        """USER SELECTED KIND OF NAILS PROCEDURE"""
        new_services["kind_nails_procedure"] = message.text[:5]

        if message.text.lower() == "ручки 💅":
            AddEvent.hands_services(message)
        elif message.text.lower() == "ніжки 👣":
            AddEvent.foots_services(message)

    @staticmethod
    def hands_services(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        manik1 = types.KeyboardButton("Манікюр гігієнічний")
        manik2 = types.KeyboardButton("Манікюр з покриттям")
        manik3 = types.KeyboardButton("Манікюр з покр + укріплення")
        manik4 = types.KeyboardButton("Нарощення")
        markup.add(manik1, manik2, manik3, manik4)
        bot.send_message(message.from_user.id, text="Оберіть, що саме вас цікавить ⬇️", reply_markup=markup)
        bot.register_next_step_handler(message, AddEvent.additions)

    @staticmethod
    def foots_services(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        pedik1 = types.KeyboardButton("Педикюр гігієнічний")
        pedik2 = types.KeyboardButton("Педикюр з покриттям")
        markup.add(pedik1, pedik2)
        bot.send_message(message.from_user.id, text="Оберіть, що саме вас цікавить ⬇️", reply_markup=markup)
        bot.register_next_step_handler(message, AddEvent.kind_of_foot_service)

    @staticmethod
    def kind_of_foot_service(message):
        new_services["services"].append(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        if message.text.lower() == "педикюр гігієнічний" or message.text.lower() == "педикюр з покриттям":
            foots_gigiena1 = types.KeyboardButton("Тільки пальчики")
            foots_gigiena2 = types.KeyboardButton("Пальчики + стопа")
            markup.add(foots_gigiena1, foots_gigiena2)
        bot.send_message(message.from_user.id, text="Оберіть, що саме вас цікавить ⬇️", reply_markup=markup)
        bot.register_next_step_handler(message, AddEvent.additions)

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
            bot.register_next_step_handler(message, AddEvent.second_event_request)
        else:
            bot.register_next_step_handler(message, AddEvent.wich_day)

    @staticmethod
    def second_event_request(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        new_services["additions"].append(message.text)
        if new_services["kind_nails_procedure"] == "Ручки":
            final_message1 = types.KeyboardButton("Хочу ще педикюр")
            final_message2 = types.KeyboardButton("Завершити запис")
            markup.add(final_message1, final_message2)
            bot.send_message(message.from_user.id, text="Бажаєте додати ще послуги?", reply_markup=markup)
            bot.register_next_step_handler(message, AddEvent.second_event)

        elif new_services["kind_nails_procedure"] == "Ніжки":
            final_message1 = types.KeyboardButton("Хочу ще манікюр")
            final_message2 = types.KeyboardButton("Завершити запис")
            markup.add(final_message1, final_message2)
            bot.send_message(message.from_user.id, text="Бажаєте додати ще послуги?", reply_markup=markup)
            bot.register_next_step_handler(message, AddEvent.second_event)

    @staticmethod
    def second_event(message):
        if message.text == "Хочу ще манікюр":
            AddEvent.hands_services(message)
        elif message.text == "Хочу ще педикюр":
            AddEvent.foots_services(message)
        else:
            AddEvent.wich_day(message)

    @staticmethod
    def wich_day(message, common=True):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        days_list = TimeOperations.get_free_dates()
        for day in days_list:
            markup.add(str(day))

        user_id = message.from_user.id

        bot.send_message(user_id, text="На який день бажаєте записатись?", reply_markup=markup)
        if common:

            bot.register_next_step_handler(message, AddEvent.select_time)

        else:
            print("false")
            bot.register_next_step_handler(message, TimeOperations.transfer_select_time)

    @staticmethod
    def select_time(message, common_stream=True):
        # select event time
        print("select time")
        if common_stream:
            visiting_time.clear()
            visiting_time["day"] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        time_points = TimeOperations.create_visiting_time()
        for point in time_points:
            markup.add(str(point))
        bot.send_message(message.from_user.id,
                         text=f"На яку годину вас записати?",
                         reply_markup=markup)
        bot.register_next_step_handler(message, AddEvent.final)

    @staticmethod
    def final(message, meeting_time=False):
        """ADD EVENT TO DB IF USER ALREADY EXISTS"""
        print(message.text)
        visiting_time["hour"] = message.text
        if not meeting_time:
            print(visiting_time["day"], visiting_time["hour"])
        new_services["user_first_name"] = message.from_user.first_name
        if not User.user_exist(message.from_user.id):
            bot.send_message(message.from_user.id,
                             text="Вкажіть ваш номер мобільного для зворотнього зв'язку",
                             reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, AddEvent.get_user_phone)
        else:
            bot.send_message(message.from_user.id,
                             text="________________________________",
                             reply_markup=types.ReplyKeyboardRemove())
            new_services["user_phone"] = User.get_user(message.from_user.id).user_mobile
            AddEvent.event_to_db(user_id=message.from_user.id, meeting_time=TimeOperations.get_visiting_datetime())

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
                User.add_user(user)
                AddEvent.event_to_db(user_id=message.from_user.id, meeting_time=datetime.utcnow())

            else:
                """IF PHONE IS NOT VALID TRY AGAIN"""
                bot.send_message(message.from_user.id, text="Ви вказали некоректний номер🤨, введіть будь ласка ще раз")
                bot.register_next_step_handler(message, AddEvent.get_user_phone)

        except AttributeError as err:
            print("Error get phone", err)
            bot.send_message(message.from_user.id, text="Ви вказали некоректиний номер🤨, введіть будьласка ще раз")
            bot.register_next_step_handler(message, AddEvent.get_user_phone)

    @staticmethod
    def event_to_db(user_id: int, meeting_time: datetime):
        time_price = TimeOperations.get_estimated_time(new_services["services"])
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
        if str(user_id) == str(admin_id):
            print("IS admin order")
            fake_user = ServiceOperations.get_fake_user()
            print(fake_user)
            User.add_user(fake_user)

            order = ServiceOperations.create_order(new_services=new_services,
                                                   user=fake_user,
                                                   time=meeting_time)

            Order.add_order(order)
            bot.send_message(user_id, f"Ви успішно записались \n"
                                      f"{order_message}")
            AddEvent.final_message(user_id)
        else:
            order = ServiceOperations.create_order(new_services=new_services, user=user_id, time=meeting_time)
            Order.add_order(order)
            bot.send_message(user_id, f"Ви успішно записались \n"
                                      f"{order_message}")
            AddEvent.final_message(user_id)

        clear_services()

    @staticmethod
    def final_message(chat_id):
        keyboard = InlineKeyboardMarkup()
        to_start = InlineKeyboardButton(text="На головну", callback_data="to_mainboard")
        bot_order = InlineKeyboardButton(text="також хочу бот", callback_data="need_bot")
        keyboard.add(to_start, bot_order)
        bot.send_message(chat_id, text="Якщо ви підприємець і вас зацікавила можливість оптимізації свого бізнесу"
                                       " за допомогою аналогічного боту або іншого продукту"
                                       " натисніть (також хочу бот)", reply_markup=keyboard)

        """And of Adding event methods block"""
