import re
import random
from datetime import datetime, timedelta

from static_data import session, Session, visiting_time
from models import User, Procedure, Order
from configs import ADMIN_ID


# temporary storage of services



class DatabaseOperations:
    def __init__(self, session: Session = session):
        self.session = session

    def add_user(self, user: User):
        session.add(user)
        session.commit()
        session.close()

    def add_procedure(self, procedure: Procedure):
        session.add(procedure)
        session.commit()
        session.close()

    def user_exist(self, user_id: int) -> bool:
        users = []
        all_users = session.query(User).all()
        for record in all_users:
            users.append(record.user_id)
        if user_id in users:
            session.close()
            return True
        else:
            session.close()
            return False

    def get_user_info(self, user_id: int) -> User:
        # Query the User table by user_id
        user_info = session.query(User).filter_by(user_id=user_id).first()
        return user_info

    def get_user_procedure(self, user_id: int) -> Order:
        user_procedure = session.query(Order).filter_by(user_id=user_id).first()
        return user_procedure

    def remove_order_record(self, user_id: int):
        order_to_delete = session.query(Order).filter(Order.user_id == user_id).first()
        session.delete(order_to_delete)
        session.commit()
        session.close()
        print(f"RECORD USER {user_id} WAS DELETE")

    def get_all_events(self) -> list:
        # return list of all created events dicts
        all_events = session.query(Order).all()
        order_dicts = []
        for event in all_events:
            usr_first_name = DatabaseOperations.get_user_info(self, event.user_id).user_first_name
            if event.procedure3 is None:
                order_dicts.append({"user_id": event.user_id,
                                    "user_first_name": usr_first_name,
                                    "date": event.meeting_time,
                                    "procedure1": event.procedure1,
                                    "procedure2": event.procedure2}
                                   )

            elif event.procedure3:
                order_dicts.append({"user_id": event.user_id,
                                    "user_first_name": usr_first_name,
                                    "date": event.meeting_time,
                                    "procedure1": event.procedure1,
                                    "procedure2": event.procedure2,
                                    "procedure3": event.procedure3}
                                   )
            elif event.procedure4:
                order_dicts.append({"user_id": event.user_id,
                                    "user_first_name": usr_first_name,
                                    "date": event.meeting_time,
                                    "procedure1": event.procedure1,
                                    "procedure2": event.procedure2,
                                    "procedure3": event.procedure3,
                                    "procedure4": event.procedure4}
                                   )
            else:
                order_dicts.append({"user_id": event.user_id,
                                    "user_first_name": usr_first_name,
                                    "date": event.meeting_time,
                                    "procedure1": event.procedure1,
                                    "procedure2": event.procedure2,
                                    "procedure3": event.procedure3,
                                    "procedure4": event.procedure4,
                                    "additions": event.additions}
                                   )

        return [order_dicts]

    def rem_selected_order(self, message):
        user_id = re.findall(r'\d+', message.text[3:15])
        try:
            DatabaseOperations.remove_order_record(session, user_id[0])
        except IndexError:
            print("Record was not deleted")
        except TypeError:
            print("Message not found")

    def remove_user(self, user_id):
        user_to_delete = session.query(User).filter(User.user_id == user_id).first()
        del_message = f"User: {user_to_delete.username}  {user_to_delete.user_first_name} was deleted"
        session.delete(user_to_delete)
        session.commit()
        session.close()
        print(del_message)

    def change_order(self, order: Order):
        order_time = order.meeting_time


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


class ServiceOperations:
    @staticmethod
    def create_order(new_services: dict, user_id: int, time) -> Order:
        """ADD PROCEDURE RECORD HAVE DIFFERENT COUNT OF PARAMETERS"""

        # create fake user_id for admin order
        if user_id == int(ADMIN_ID):
            fake_user = ServiceOperations.get_fake_user()
            DatabaseOperations.add_user(session, fake_user)

        if len(new_services["services"]) + len(new_services["additions"]) == 2:
            order = Order(
                user_id=user_id,
                meeting_time=time,
                kind_nails_service=["kind_nails_procedure"][:5],
                procedure1=new_services["services"][0],
                additions=new_services["additions"][0],
            )
        elif len(new_services["services"]) + len(new_services["additions"]) == 3:
            order = Order(
                user_id=user_id,
                kind_nails_service=time,
                procedure1=new_services["services"][0],
                procedure2=new_services["services"][1],
                additions=new_services["additions"][0],
            )
        elif len(new_services["services"]) + len(new_services["additions"]) == 4:
            order = Order(
                user_id=user_id,
                kind_nails_service=time,
                procedure1=new_services["services"][0],
                procedure2=new_services["services"][1],
                additions=new_services["additions"][0],
                procedure4=new_services["additions"][1],
            )
        else:
            order = Order(
                user_id=user_id,
                kind_nails_service=time,
                procedure1=new_services["services"][0],
                procedure2=new_services["services"][1],
                procedure3=new_services["services"][2],
                procedure4=new_services["additions"][0],
                additions=new_services["additions"][1]
            )
        return order

    @staticmethod
    def is_valid_phone(phone: str) -> bool or str:
        standart_phone = str(phone.replace("+38", ""))
        if standart_phone.isdigit() and len(standart_phone) == 10 and standart_phone.startswith("0"):
            return standart_phone
        else:
            return False

    @staticmethod
    def create_order_info(order: Order) -> dict:
        first_name = DatabaseOperations.get_user_info(session, order.user_id).user_first_name
        user_phone = DatabaseOperations.get_user_info(session, order.user_id).user_mobile
        meeting_time = order.meeting_time
        new_services = {"services": [],
                        "additions": [],
                        "first_name": first_name,
                        "time": meeting_time,
                        "user_phone": user_phone}
        new_services["services"].append(order.procedure1)
        new_services["additions"].append(order.additions)
        if order.procedure2:
            new_services["services"].append(order.procedure2)
        if order.procedure3:
            new_services["services"].append(order.procedure3)
        if order.procedure4:
            new_services["additions"].append(order.procedure4)
        return new_services

    @staticmethod
    def get_fake_user(username="fakeuser",
                      first_name="fakeuser",
                      last_name="fakeuser",
                      mobile="067576767") -> User:
        random_number = random.randint(100000, 999999)
        exist = DatabaseOperations.user_exist(session, random_number)
        if exist:
            random_number2 = random.randint(100000, 999999)
            user_id = random_number2
        else:
            user_id = random_number
        fake_user = User(user_id=user_id,
                         username=username,
                         first_name=first_name,
                         last_name=last_name,
                         mobile=mobile)
        return fake_user


def get_estimated_time(procedures: list) -> dict:
    estimate_time = 0
    estimate_price = 0
    for procedure in procedures:
        print(procedure)
        estimate_time += Procedure.get_procedure(proc_name=procedure).proc_time
        estimate_price += Procedure.get_procedure(proc_name=procedure).proc_price

    return {"estim_time": estimate_time,
            "estim_price": estimate_price}


def create_datetime(visiting_time: dict) -> datetime:
    year = int(f"20{visiting_time['day'][6:8]}")
    month = int(visiting_time['day'][3:5])
    day = int(visiting_time['day'][0:2])
    hour = int(visiting_time['hour'][0:2])
    minute = int(visiting_time['hour'][3:5])
    new_datetime = datetime(year, month, day, hour, minute)
    return new_datetime


def _add_test_user():
    user = User(user_id=1587874848,
                username="username",
                first_name="first_name",
                last_name="last_name",
                mobile="986785474")
    DatabaseOperations.add_user(session, user)


if __name__ == '__main__':
    DatabaseOperations.remove_user(session, "6565405695")
