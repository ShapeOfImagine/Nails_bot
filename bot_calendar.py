from datetime import time, timedelta, date
from static_data import session
from models import WeekShedule, DefaultWeek

week = {"Sunday": "Неділя",
        "Monday": "Понеділок",
        "Tuesday": "Вівторок",
        "Wednesday": "Середа",
        "Thursday": "Четвер",
        "Friday": "П'ятниця",
        "Saturday": "Субота"}

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


for default_day in DefaultWeek.get_all_week():
    print(default_day)




