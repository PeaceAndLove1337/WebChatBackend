from typing import Optional

from werkzeug.security import generate_password_hash

from data.db_models import User, db, Session, Chat, Message
from data.db_queries import take_user_id_by_api_key
from domain.business_logic import generate_api_key_by_time, take_time_at_now_without_ms, take_time_at_now, \
    take_time_at_now_with_delta_one_day


def add_new_user_in_db(curr_login: str, curr_password: str) -> bool:
    user = User(
        login=curr_login,
        password=generate_password_hash(curr_password)
    )
    try:
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as e:
        print(type(e))
        print(e.args)
        return False


def add_new_session_in_db(curr_user_data: User) -> Optional[str]:
    curr_api_key_str = generate_api_key_by_time(take_time_at_now())
    new_session = Session(
        user_id=curr_user_data.user_id,
        api_key=curr_api_key_str,
        expired_date=take_time_at_now_with_delta_one_day()
    )
    try:
        db.session.add(new_session)
        db.session.commit()
        return curr_api_key_str
    except Exception as e:
        print(type(e))
        print(e.args)
        return None


def add_new_chat_in_db(curr_api_key: str, curr_chat_name: str) -> bool:
    new_chat = Chat(
        user_id=take_user_id_by_api_key(curr_api_key),
        chat_name=curr_chat_name
    )
    try:
        db.session.add(new_chat)
        db.session.commit()
        return True
    except Exception as e:
        print(type(e))
        print(e.args)
        return False


def add_new_message_in_chat_in_db(curr_api_key: str, curr_chat_id: int, curr_message_body: str) -> bool:
    curr_user_id = take_user_id_by_api_key(curr_api_key)
    new_message = Message(
        chat_id=curr_chat_id,
        user_id=curr_user_id,
        time_data=take_time_at_now_without_ms(),
        message_body=curr_message_body
    )
    try:
        db.session.add(new_message)
        db.session.commit()
        return True
    except Exception as e:
        print(type(e))
        print(e.args)
        return False
