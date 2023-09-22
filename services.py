import re
import random

from static_data import session, Session
from models import User, Order
from configs import ADMIN_ID


class DatabaseOperations:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all_events(self) -> list:
        # return list of all created events dicts
        all_events = session.query(Order).all()
        order_dicts = []
        for event in all_events:
            usr_first_name = User.get_user(event.user_id).user_first_name
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
            Order.remove_order_record(user_id[0])
        except IndexError:
            print("Record was not deleted")
        except TypeError:
            print("Message not found")

    def change_order(self, order: Order):
        order_time = order.meeting_time


class ServiceOperations:
    @staticmethod
    def create_order(new_services: dict, user_id: int, time) -> Order:
        """ADD PROCEDURE RECORD HAVE DIFFERENT COUNT OF PARAMETERS"""

        # create fake user_id for admin order
        if user_id == int(ADMIN_ID):
            fake_user = ServiceOperations.get_fake_user()
            User.add_user(fake_user)

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
        first_name = User.get_user(order.user_id).user_first_name
        user_phone = User.get_user(order.user_id).user_mobile
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
        exist = User.user_exist(random_number)
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


def _add_test_user():
    user = User(user_id=1587874848,
                username="username",
                first_name="first_name",
                last_name="last_name",
                mobile="986785474")
    User.add_user(user)


if __name__ == '__main__':
    User.remove_user("6565405695")
