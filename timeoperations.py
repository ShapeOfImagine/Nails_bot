from telebot import types
from datetime import datetime, timedelta
from models import Procedure, Order
from static_data import bot, visiting_time, session, calendar
from services import DatabaseOperations


class TimeOperations:

    week = {"Sunday": "Неділя",
            "Monday": "Понеділок",
            "Tuesday": "Вівторок",
            "Wednesday": "Середа",
            "Thursday": "Четвер",
            "Friday": "П'ятниця",
            "Saturday": "Субота"}

    @staticmethod
    def get_visiting_datetime() -> datetime:
        date_string = f"{visiting_time['day']} {visiting_time['hour']}"
        format_string = '%d.%m.%y %H:%M'
        datetime_object = datetime.strptime(date_string, format_string)
        return datetime_object

    @staticmethod
    def create_visiting_time() -> list:
        start_time = datetime.strptime("15:00", "%H:%M")
        time_points = []
        # will generate 4 time points at intervals of hour
        for i in range(4):
            time_points.append(start_time.strftime("%H:%M"))
            start_time += timedelta(hours=1)

        return time_points

    @staticmethod
    def change_order_time(order: Order, meeting_time):
        order.update_meeting_time(meeting_time)
        print(f"Дату процедури користувача {order.user_id} Змінено на {meeting_time}")

    @staticmethod
    def get_free_dates() -> list:
        today = datetime.today()
        next_days = []
        reserved_dates = []
        events = DatabaseOperations.get_all_events(session)[0]
        for event in events:
            reserved_dates.append(event["date"].strftime("%d.%m.%y"))
        if today.strftime("%d.%m.%y") not in reserved_dates:
            next_days.append(today.strftime("%d.%m.%y"))

        for i in range(1, 10):
            next_date = today + timedelta(days=i)
            if next_date.strftime("%d.%m.%y") not in reserved_dates:
                next_days.append(next_date.strftime("%d.%m.%y"))
        return next_days

    @staticmethod
    def rem_past_events():
        events = DatabaseOperations.get_all_events(session)[0]
        count = 0
        for event in events:
            if event["date"] < datetime.now():
                DatabaseOperations.remove_order_record(session, event["user_id"])
                count += 1
        print(f"{count} past events was deleted")

    @staticmethod
    def get_order_by_date(target_date):
        if not isinstance(target_date, datetime):
            target_date = datetime.combine(target_date, datetime.min.time())

        try:
            events = DatabaseOperations.get_all_events(session)[0]
            for event in events:
                if event["date"].strftime("%d.%m.%y") == target_date.strftime("%d.%m.%y"):
                    return event
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
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
        bot.register_next_step_handler(message, TimeOperations.transfer_event_set_time)

    @staticmethod
    def transfer_event_set_time(message):
        visiting_time["hour"] = message.text
        new_time = TimeOperations.create_datetime(visiting_time)
        order = DatabaseOperations.get_user_procedure(session, message.from_user.id)
        TimeOperations.change_order_time(order=order, meeting_time=new_time)
        bot.send_message(message.from_user.id,
                         text=f"Запис успішно перенесено на "
                              f"{TimeOperations.week[order.meeting_time.strftime('%A')]} "
                              f"{order.meeting_time.strftime('%d.%m %H:%M')}",
                         reply_markup=types.ReplyKeyboardRemove())
    @staticmethod
    def create_datetime(visiting_time: dict) -> datetime:
        year = int(f"20{visiting_time['day'][6:8]}")
        month = int(visiting_time['day'][3:5])
        day = int(visiting_time['day'][0:2])
        hour = int(visiting_time['hour'][0:2])
        minute = int(visiting_time['hour'][3:5])
        new_datetime = datetime(year, month, day, hour, minute)
        return new_datetime

    @staticmethod
    def get_estimated_time(procedures: list) -> dict:
        estimate_time = 0
        estimate_price = 0
        for procedure in procedures:
            print(procedure)
            estimate_time += Procedure.get_procedure(proc_name=procedure).proc_time
            estimate_price += Procedure.get_procedure(proc_name=procedure).proc_price

        return {"estim_time": estimate_time,
                "estim_price": estimate_price}
