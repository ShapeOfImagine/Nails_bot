from datetime import time, timedelta, date
from telebot import types
from static_data import session, bot
from services import ServiceOperations
from models import WeekShedule, DefaultWeek
from configs import ADMIN_ID


week = {"Sunday": "Неділя",
        "Monday": "Понеділок",
        "Tuesday": "Вівторок",
        "Wednesday": "Середа",
        "Thursday": "Четвер",
        "Friday": "П'ятниця",
        "Saturday": "Субота"}

selected_day = ""
part_day = ""
parts_day = {"change_start_day": "початок дня",
             "change_end_day": "кінець дня",
             "break_start": "початок кава брейку",
             "break_duration": "тривалість кава брейку"}


default_start_time = time(12, 0)
default_end_time = time(19, 0)
start_break = time(15, 0)
coffe_break = timedelta(minutes=30)
week_duration = timedelta(days=7)
start_week = date(2023, 9, 25)
#
# for day in week:
#     day_of_week = str(week[day])
#     default_day = DefaultWeek(
#                             day_of_week=day_of_week,
#                             start_time=default_start_time,
#                             end_time=default_end_time,
#                             start_coffee_break=start_break,
#                             coffee_break_duration=coffe_break
#                             )
#     DefaultWeek.add_week_day(default_day)


class CalendarHandlers:

    @staticmethod
    def week_settings_sel_day(call: types.CallbackQuery):
        week = DefaultWeek.get_all_week()
        keyboard = types.InlineKeyboardMarkup()
        for day in week:
            keyboard.add(types.InlineKeyboardButton(text=day.day_of_week, callback_data=day.day_of_week))
        bot.send_message(ADMIN_ID,
                         text="Виберіть день розклад за замовчуванням якогого хотіли б змінити\n"
                              "Зміни будуть збережені і за цим розкладом будуть будуватись "
                              "наступні тижні",
                         reply_markup=keyboard)

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data in week.values())
    def set_day(call):
        day = DefaultWeek.get_day(call.data)

        # set day
        global selected_day
        selected_day = day.day_of_week

        keyboard = types.InlineKeyboardMarkup()
        change_start_day = types.InlineKeyboardButton(text="Початок дня", callback_data="change_start_day")
        change_end_day = types.InlineKeyboardButton(text="Кінець дня", callback_data="change_end_day")
        break_start = types.InlineKeyboardButton(text="Початок брейку", callback_data="break_start")
        break_duration = types.InlineKeyboardButton(text="Тривалість брейку", callback_data="break_duration")
        full_refactor = types.InlineKeyboardButton(text="Переробити весь розклад", callback_data="full_refactor")
        keyboard.add(change_start_day, change_end_day, break_start, break_duration, full_refactor)
        bot.send_message(ADMIN_ID, text=day)
        bot.send_message(ADMIN_ID,
                         text="Виберіть що саме змінти \n (початок дня, кінець дня, початок кава брейку, "
                              "тривалість кава брейку, або повністю змінити розклад",
                         reply_markup=keyboard)

    @staticmethod
    @bot.callback_query_handler(func=lambda call:
                                call.data == "change_start_day" or call.data == "break_start"
                                or call.data == "change_end_day" or call.data == "break_duration")
    def get_start_day(call):
        day = DefaultWeek.get_day(selected_day)

        # set selected part day
        global part_day
        if isinstance(call, types.CallbackQuery):
            part_day = call.data
            part_day_mess = parts_day[call.data]
        else:
            part_day = call.text
            part_day_mess = parts_day[call.text]

        if part_day != "break_duration":
            bot.send_message(ADMIN_ID, text=f"Відправте новий {part_day_mess} на {day.day_of_week}\n"
                                            f"Формат: 10:01 ")
        else:
            bot.send_message(ADMIN_ID, text=f"напишіть {part_day_mess} на {day.day_of_week}\n"
                                            f"Формат: 1:30 \n"
                                            f"Де 1 кількіть годин, 30 кількість хвилин")

        if isinstance(call, types.Message):
            bot.register_next_step_handler(call, CalendarHandlers.set_new_start_day)
        else:
            message = ServiceOperations.callback_convert(call)
            bot.register_next_step_handler(message, CalendarHandlers.set_new_start_day)

    @staticmethod
    def set_new_start_day(message):
        day = DefaultWeek.get_day(selected_day)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        to_start = types.KeyboardButton('/start')
        select_day = types.KeyboardButton(text="Змінити ще день")
        markup.add(to_start, select_day)

        if part_day != "break_duration":
            mess_time = ServiceOperations.mess_to_time(message.text)
            if mess_time:
                print(part_day)
                if part_day == "change_start_day":
                    DefaultWeek.update_start_time(day, mess_time)
                elif part_day == "change_end_day":
                    DefaultWeek.update_end_day(day, mess_time)
                elif part_day == "break_start":
                    DefaultWeek.update_start_break(day, mess_time)
                bot.send_message(ADMIN_ID,
                                 text=f"{parts_day[part_day]} {day.day_of_week} Успішно змінено",
                                 reply_markup=markup)
            else:
                bot.send_message(ADMIN_ID, text="Неправильний формат часу, спробуйте знову\n"
                                                "Вкажіть годину потім : потім хвилини")
                CalendarHandlers.get_start_day(message)
        else:
            delta = ServiceOperations.mess_to_timedelta(message.text)
            if delta:
                DefaultWeek.update_break_duration(day, delta)
                bot.send_message(ADMIN_ID,
                                 text=f"{parts_day[part_day]} {day.day_of_week} Успішно змінено",
                                 reply_markup=markup)
            else:
                bot.send_message(ADMIN_ID, text="Неправильний формат часу, спробуйте знову\n"
                                                "Вкажіть годину потім : потім хвилини")
                CalendarHandlers.get_start_day(message)


@bot.message_handler(func=lambda message: message.text == "Змінити ще день")
def select_day_pool(message):
    CalendarHandlers.week_settings_sel_day(message)
