from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from static_data import session, db_url

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
        self.user_id = user_id
        self.username = username
        self.user_first_name = first_name
        self.user_last_name = last_name
        self.user_mobile = mobile


class Procedure(Base):
    """Manicure procedures list"""
    __tablename__ = "procedure"

    proc_name = Column(String, unique=True, primary_key=True)
    proc_price = Column(Integer)
    proc_time = Column(Integer)

    def __init__(self, proc_name, proc_price, proc_time):
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


class ProcedurePedikure(Base):

    __tablename__ = "procedure_pedikure"

    proc_name = Column(String, unique=True, primary_key=True)
    proc_price = Column(Integer)
    proc_time = Column(Integer)

    def __init__(self, proc_name, proc_price, proc_time):
        self.proc_name = proc_name
        self.proc_price = proc_price
        self.proc_time = proc_time

    def add_procedure(self):
        session.add(self)
        session.commit()
        session.close()

    @staticmethod
    def get_procedure(proc_name: str):
        procedure = session.query(ProcedurePedikure).filter_by(proc_name=proc_name).first()
        return procedure


class Addition(Base):

    __tablename__ = "additions"

    addition_name = Column(String, unique=True, primary_key=True)
    addition_price = Column(Integer)
    addition_time = Column(Integer)

    def __init__(self, addition_name, addition_price, addition_time):
        self.addition_name = addition_name
        self.addition_price = addition_price
        self.addition_time = addition_time


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
        self.user_id = user_id
        self.meeting_time = meeting_time or datetime.utcnow()
        self.kind_nails_service = kind_nails_service
        self.procedure1 = procedure1
        self.procedure2 = procedure2
        self.procedure3 = procedure3
        self.procedure4 = procedure4
        self.additions = additions

    def update_meeting_time(self, new_meeting_time):
        self.meeting_time = new_meeting_time



# Base.metadata.create_all(engine)
#
#
# procedure = Procedure(
#     proc_name="Педикюр гігієнічний",
#     proc_price=100,
#     proc_time=2
#
# )
#
# Procedure.add_procedure(procedure)
# print(proc)
# print(get_procedure("Нарощення").proc_price)