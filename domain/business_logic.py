import hashlib
import datetime


def take_time_at_now():
    return datetime.datetime.now()


def take_time_at_now_with_delta_one_day():
    return take_time_at_now() + datetime.timedelta(days=1)


def take_time_at_now_without_ms() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_api_key_by_time(curr_time) -> str:
    return hashlib.md5(str(curr_time).encode()).hexdigest()


def is_entered_date_less_than_curr_time(date) -> bool:
    return date < datetime.datetime.now()
