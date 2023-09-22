from datetime import time, timedelta
from static_data import session
from models import WeekShedule, DayShedule

week = {"Sunday": "Неділя",
        "Monday": "Понеділок",
        "Tuesday": "Вівторок",
        "Wednesday": "Середа",
        "Thursday": "Четвер",
        "Friday": "П'ятниця",
        "Saturday": "Субота"}

default_start_time = time(12, 0)
default_end_time = time(19, 0)
coffe_break = timedelta(minutes=30)
week_duration = timedelta(days=7)

for day in week:
    day_of_week = str(week[day])
    default_day = WeekShedule(
                            day_of_week=day_of_week,
                            start_time=default_start_time,
                            end_time=default_end_time,
                            coffe_break=coffe_break,
                            week_duration=week_duration)
    session.add(default_day)
    session.commit()
    print(default_day)