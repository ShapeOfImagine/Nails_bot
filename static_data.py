import telebot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configs import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, TOKEN

db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()
session = Session()
bot = telebot.TeleBot(TOKEN)

new_services = {"services": [],
                "additions": []}

visiting_time = {}

calendar = {"1": "Січня",
            "2": "Лютого",
            "3": "Березня",
            "4": "Квітня",
            "5": "Травня",
            "6": "Червня",
            "7": "Липня",
            "8": "Серпня",
            "9": "Вересня",
            "10": "Жовтня",
            "11": "Листопада",
            "12": "Грудня"}