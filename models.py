from sqlalchemy import create_engine, Column, Integer, String, \
    ForeignKey, DateTime, BigInteger, Boolean, Date, Time, Interval
from sqlalchemy import MetaData, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists
from datetime import datetime, timedelta, time, date
from static_data import session, db_url, Session, week

engine = create_engine(db_url)

Base = declarative_base()


def _test_connect():
    try:
        connection = engine.connect()
        print("Connected successfully!")

        connection.close()
    except Exception as ex:
        print("Connection failed:", ex)


class User(Base):

    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True, unique=True)
    username = Column(String)
    user_first_name = Column(String)
    user_last_name = Column(String)
    user_mobile = Column(String)

    def __init__(self, user_id, username, first_name, last_name, mobile):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.user_first_name = first_name
        self.user_last_name = last_name
        self.user_mobile = mobile

    def __str__(self):
        user_string = f"""
        ID: {self.user_id}\n
        username: {self.username}\n
        first_name: {self.user_first_name}\n
        last_name: {self.user_last_name}\n
        mobile: {self.user_mobile}"""
        return user_string

    def add_user(self):
        session = Session()
        session.add(self)
        session.commit()
        session.close()

    @staticmethod
    def get_user(user_id: int):
        user = session.query(User).filter_by(user_id=user_id).first()
        return user

    @staticmethod
    def user_exist(user_id: int) -> bool:
        stmt = exists().where(User.user_id == user_id)
        result = session.query(stmt).scalar()
        session.close()

        if result:
            return True

        else:
            return False

    @staticmethod
    def remove_user(user_id):
        user_to_delete = User.get_user(user_id)
        del_message = f"User: {user_to_delete.username}  {user_to_delete.user_first_name} was deleted"
        session.delete(user_to_delete)
        session.commit()
        session.close()
        print(del_message)


class Procedure(Base):
    """Manicure procedures list"""
    __tablename__ = "procedure"

    proc_name = Column(String, unique=True, primary_key=True)
    proc_price = Column(Integer)
    proc_time = Column(Integer)

    def __init__(self, proc_name, proc_price, proc_time):
        super().__init__()
        self.proc_name = proc_name
        self.proc_price = proc_price
        self.proc_time = proc_time

    def add_procedure(self):
        session.add(self)
        session.commit()
        session.close()

    @staticmethod
    def get_all() -> list:
        all_items = session.query(Procedure).all()
        return all_items

    @staticmethod
    def get_procedure(proc_name: str):
        procedure = session.query(Procedure).filter_by(proc_name=proc_name).first()
        return procedure


class Addition(Base):

    __tablename__ = "additions"

    addition_name = Column(String, unique=True, primary_key=True)
    addition_price = Column(Integer)
    addition_time = Column(Integer)

    def __init__(self, addition_name, addition_price, addition_time):
        super().__init__()
        self.addition_name = addition_name
        self.addition_price = addition_price
        self.addition_time = addition_time

    def add_addition(self):
        session.add(self)
        session.commit()
        session.close()

    @staticmethod
    def get_addition(addi_name: str):
        addition = session.query(Addition).filter_by(addition_name=addi_name).first()
        return addition


class Order(Base):

    __tablename__ = "order"

    user_id = Column(BigInteger, ForeignKey("user.user_id"), primary_key=True)
    meeting_time = Column(DateTime, default=datetime.utcnow)
    kind_nails_service = Column(String)
    procedure1 = Column(String)
    procedure2 = Column(String, default=False)
    procedure3 = Column(String, default=False)
    procedure4 = Column(String, default=False)
    additions = Column(String)

    def __init__(self, user_id, kind_nails_service,
                 procedure1, procedure2=False, procedure3=False,
                 procedure4=False, additions=False, meeting_time=None):
        super().__init__()
        self.user_id = user_id
        self.meeting_time = meeting_time or datetime.utcnow()
        self.kind_nails_service = kind_nails_service
        self.procedure1 = procedure1
        self.procedure2 = procedure2
        self.procedure3 = procedure3
        self.procedure4 = procedure4
        self.additions = additions

    def __str__(self):
        user = User.get_user(self.user_id)
        user_first_name = user.user_first_name
        user_phone = user.user_mobile
        default_message = f"""Замовлення:  {user_first_name} Мобільний: {user_phone}\nЧас прийому: {self.meeting_time.strftime("%d.%m.%y  %H:%M")}\nПроцедура: {self.procedure1}\nДодатки: {self.additions}\
                           """
        intermediate_procedure = f"{self.procedure2}"
        intermediate_procedure2 = f"{self.procedure3}"
        second_procedure = f"Друга процедура: {self.procedure2}\nДодатки: {self.procedure4}"
        if self.procedure2 != "false" and self.procedure4 != "false":
            return default_message + second_procedure
        elif self.procedure2 != "false" and self.procedure4 == "false":
            return default_message + intermediate_procedure
        elif self.procedure3 != "false":
            return default_message + intermediate_procedure2 + second_procedure
        else:
            return default_message

    def add_order(self):
        session.add(self)
        session.commit()
        session.close()

    @staticmethod
    def get_user_order(user_id):
        order = session.query(Order).filter_by(user_id=user_id).first()
        return order

    @staticmethod
    def get_orders_by_date(order_date: date) -> list or bool:
        orders = session.query(Order).filter(func.date(Order.meeting_time) == order_date).all()
        if len(orders) > 0:
            return orders
        else:
            return False

    @staticmethod
    def remove_order_record(user_id: int):
        order_to_delete = session.query(Order).filter(Order.user_id == user_id).first()
        if order_to_delete:
            session.delete(order_to_delete)
            session.commit()
            session.close()
            print(f"RECORD USER {user_id} WAS DELETE")
        else:
            print("rem oder unsucces Order by user_id not found")

    def update_meeting_time(self, new_meeting_time):
        self.meeting_time = new_meeting_time


class DefaultWeek(Base):

    __tablename__ = "default_week"

    id = Column(Integer, primary_key=True)
    day_of_week = Column(String(20), unique=True, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    start_coffee_break = Column(Time)
    coffee_break_duration = Column(Interval)
    is_working = Column(Boolean)

    def __init__(self, day_of_week, start_time, end_time, start_coffee_break, coffee_break_duration, is_working):
        super().__init__()
        self.day_of_week = day_of_week
        self.is_working = is_working
        self.start_time = datetime.combine(datetime.today(), start_time)
        self.end_time = datetime.combine(datetime.today(), end_time)
        self.day_duration = self.end_time - self.start_time
        self.start_coffee_break = datetime.combine(datetime.today(), start_coffee_break)
        self.coffee_break_duration = coffee_break_duration

        self.end_coffee_break = self.start_coffee_break + self.coffee_break_duration

    def __str__(self):
        end_coffee_break = datetime.combine(datetime.today(), self.start_coffee_break) + self.coffee_break_duration
        str_represent = f"""
        День тижня: {self.day_of_week}\n
        Робочий день починається: {self.start_time.strftime('%H:%M')}\n
        Робочий день закінчується: {self.end_time.strftime('%H:%M')}\n
        Початок кава брейку: {self.start_coffee_break.strftime('%H:%M')}\n
        Кінець кава брейку: {end_coffee_break.strftime('%H:%M')}
        """
        return str_represent

    def add_week_day(self):
        session.add(self)
        session.commit()
        session.close()

    def update_start_time(self, new_start_time: time):
        self.start_time = new_start_time

    def update_end_day(self, new_end_day: time):
        self.end_time = new_end_day

    def update_start_break(self, new_start_break: time):
        self.start_coffee_break = new_start_break

    def update_break_duration(self, new_break_duration):
        self.coffee_break_duration = new_break_duration

    @staticmethod
    def clear_default_shedule():
        session.query(DefaultWeek).delete()
        session.commit()
        session.close()

    @staticmethod
    def get_day(day_of_week):
        return session.query(DefaultWeek).filter_by(day_of_week=day_of_week).first()

    @staticmethod
    def set_day(day_of_week, start_time,
                end_time, start_coffee_break, coffee_break_duration):
        day = DefaultWeek.get_day(day_of_week)
        day.start_time = start_time
        day.end_time = end_time
        day.start_coffee_break = start_coffee_break
        day.coffee_break_duration = coffee_break_duration

    @staticmethod
    def get_all_week():
        return session.query(DefaultWeek).all()


class DayShedule(Base):

    __tablename__ = "day_shedule"

    id = Column(Integer, primary_key=True)
    day_of_week = Column(String(20), nullable=False)
    calendar_day = Column(Date, unique=True)
    is_working = Column(Boolean, nullable=False, default=True)   # or not working day
    start_time = Column(Time)
    end_time = Column(Time)
    start_coffee_break = Column(Time)
    coffe_break_duration = Column(Interval)

    # week_schedule = relationship('WeekSchedule', backref='days')

    def add_day(self):
        session.add(self)
        session.commit()
        session.close()

    @staticmethod
    def get_day(date: date):
        day = session.query(DayShedule).filter_by(calendar_day=date).first()
        if day:
            return day
        else:
            return False

    @staticmethod
    def create_self(date: date):
        day_of_week = week[date.strftime("%A")]
        default_day = session.query(DefaultWeek).filter_by(day_of_week=day_of_week).first()
        day = DayShedule(
            day_of_week=day_of_week,
            calendar_day=date,
            start_time=default_day.start_time,
            end_time=default_day.end_time,
            start_coffe_break=default_day.start_coffee_break,
            coffee_break_duration=default_day.coffee_break_duration,
            is_working=True

        )
        return day

    @staticmethod
    def get_all_shedule():
        shedule = session.query(DayShedule).all()
        return shedule

    def __init__(self, calendar_day, start_time, end_time, start_coffe_break,
                 coffee_break_duration, day_of_week, is_working=True):
        super().__init__()
        self.is_working = is_working
        self.day_of_week = day_of_week
        self.calendar_day = calendar_day
        self.start_time = start_time
        self.end_time = end_time
        self.start_coffe_break = start_coffe_break
        self.coffe_break_duration = coffee_break_duration

    def __str__(self):
        rep_string = f"""
            {self.day_of_week}\n
            {self.calendar_day.strftime('%d.%m.%y')}\n
            День робочий: {self.is_working}\n
            Початок дня: {self.start_time}\n
            Кінець дня: {self.end_time}"""
        return rep_string


new_metadata = MetaData()
new_metadata.reflect(bind=engine)
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# #
# procedure = Procedure(
#     proc_name="Тільки пальчики",
#     proc_price=100,
#     proc_time=2
#
# )
# #
# Procedure.add_procedure(procedure)
# print(proc)
# print(get_procedure("Нарощення").proc_price)
