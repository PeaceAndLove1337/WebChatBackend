import datetime
import hashlib

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# region models


class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)

    def __repr__(self):
        return '<User %r' % self.login


class Session(db.Model):
    __tablename__ = 'Sessions'
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=False)
    api_key = db.Column(db.String(32), nullable=False)
    expired_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Session %r' % self.session_id


class Chat(db.Model):
    __tablename__ = 'Chats'
    chat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=False)
    chat_name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Chat %r' % self.chat_id


class Message(db.Model):
    __tablename__ = 'Messages'
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("Chats.chat_id"),  nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"),  nullable=False)
    time_data = db.Column(db.String, nullable=False)
    message_body = db.Column(db.String(400), nullable=False)

    def __repr__(self):
        return '<Message %r' % self.session_id


# endregion


# region db transactions

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


def add_new_session_in_db(curr_user_data: User) -> str:
    curr_api_key_str = generate_api_key_by_time(datetime.datetime.now())
    new_session = Session(
        user_id=curr_user_data.user_id,
        api_key=curr_api_key_str,
        expired_date=datetime.datetime.now() + datetime.timedelta(days=1)
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


# endregion

# region queries
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
    elif curr_session.expired_date < datetime.datetime.now():
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
    return Message.query\
        .filter_by(chat_id=chat_id)\
        .order_by(Message.message_id)\
        .all()\
        [-count:]


def take_message_by_message_id(message_id: int) -> Message:
    return Message.query.filter_by(message_id=message_id)


def take_messages_in_chat_after_message_id(chat_id: int, message_id: int, count: int) -> list:
    return Message.query \
        .filter_by(chat_id=chat_id) \
        .filter(Message.message_id > message_id) \
        .order_by(Message.message_id).all()\
        [:count]


def take_messages_in_chat_before_message_id(chat_id: int, message_id: int, count: int) -> list:
    return Message.query \
        .filter_by(chat_id=chat_id) \
        .filter(Message.message_id < message_id) \
        .order_by(Message.message_id).all()\
        [-count:]


# endregion


# region business logic


def take_time_at_now_without_ms() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_api_key_by_time(curr_time) -> str:
    return hashlib.md5(str(curr_time).encode()).hexdigest()

# endregion
