from application.data.db_models import User, Session, Chat, Message
from application.domain.business_logic import is_entered_date_less_than_curr_time


def take_user_by_login(curr_login: str) -> User:
    return User.query \
        .filter_by(login=curr_login) \
        .first()


def take_user_name_by_user_id(user_id: int) -> str:
    return User.query \
        .filter_by(user_id=user_id) \
        .first() \
        .login


def take_user_id_by_api_key(api_key: str) -> int:
    return Session.query \
        .filter_by(api_key=api_key) \
        .first() \
        .user_id


def is_api_key_working(api_key: str) -> bool:
    curr_session = Session.query \
        .filter_by(api_key=api_key) \
        .first()

    if curr_session is None:
        return False
    elif is_entered_date_less_than_curr_time(curr_session.expired_date):
        return False
    else:  # todo нужно апдейтнуть сeссию на сутки, тк юзер активен
        return True


def take_last_user_session_by_user(user: int) -> Session:
    return Session.query \
        .filter_by(user_id=user.user_id) \
        .order_by(Session.expired_date.desc()) \
        .first()


def take_all_chats() -> list:
    return Chat.query.all()


def take_chat_by_id(chat_id: int) -> Chat:
    return Chat.query \
        .filter_by(chat_id=chat_id) \
        .first()


def take_last_messages_in_chat(chat_id: int, count: int) -> list:
    return Message.query \
               .filter_by(chat_id=chat_id) \
               .order_by(Message.message_id) \
               .all() \
        [-count:]


def take_message_by_message_id(message_id: int) -> Message:
    return Message.query.filter_by(message_id=message_id)


def take_messages_in_chat_after_message_id(chat_id: int, message_id: int, count: int) -> list:
    return Message.query \
               .filter_by(chat_id=chat_id) \
               .filter(Message.message_id > message_id) \
               .order_by(Message.message_id).all() \
        [:count]


def take_messages_in_chat_before_message_id(chat_id: int, message_id: int, count: int) -> list:
    return Message.query \
               .filter_by(chat_id=chat_id) \
               .filter(Message.message_id < message_id) \
               .order_by(Message.message_id).all() \
        [-count:]
