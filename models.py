import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configs import DB_USER, DB_NAME, DB_HOST, DB_PASSWORD
from datetime import datetime

db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
sqliteurl = "'sqlite:////home/salamandra/PycharmProjects/pythonProject/db1.db'"
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

    __tablename__ = "procedure"

    proc_name = Column(String, unique=True, primary_key=True)
    proc_price = Column(Integer)
    proc_time = Column(Integer)

    def __init__(self, proc_name, proc_price, proc_time):
        self.proc_name = proc_name
        self.proc_price = proc_price
        self.proc_time = proc_time


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


Session = sessionmaker(bind=engine)
session = Session()


Base.metadata.create_all(engine)
