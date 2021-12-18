import datetime
import hashlib

import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webchat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, resources={r'/*': {'origins': '*'}})

db = SQLAlchemy(app)


# region models


class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(102), nullable=False)

    def __repr__(self):
        return '<User %r' % self.login


class Chat(db.Model):
    __tablename__ = 'Chats'
    chat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    chat_name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Chat %r' % self.chat_id


class Session(db.Model):
    __tablename__ = 'Sessions'
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    api_key = db.Column(db.String(32), nullable=False)
    expired = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Session %r' % self.session_id


class Message(db.Model):
    __tablename__ = 'Messages'
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    time_data = db.Column(db.String, nullable=False)
    message_body = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Message %r' % self.session_id


# endregion

# region business logic


def take_user_id_by_api_key(api_key: str):
    return Session.query \
        .filter_by(api_key=api_key) \
        .first() \
        .user_id


def take_user_name_by_user_id(user_id: int):
    return User.query \
        .filter_by(user_id=user_id) \
        .first() \
        .login


def take_time_at_now_without_ms():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_api_key_by_time(curr_time):
    return hashlib.md5(str(curr_time).encode()).hexdigest()


def is_api_key_working(api_key: str):
    curr_session = Session.query \
        .filter_by(api_key=api_key) \
        .first()

    if curr_session is None:
        return False
    elif curr_session.expired < datetime.datetime.now():
        return False
    else:
        return True


def take_chat_by_id(chat_id):
    return Chat.query \
        .filter_by(chat_id=chat_id) \
        .first()


# endregion

# region routes


@app.route('/register', methods=['POST'])
def register():
    if request.method == "POST":

        json = request.get_json()
        curr_login = json["login"]
        curr_password = json["password"]
        user = User(
            login=curr_login,
            password=generate_password_hash(curr_password)
        )

        try:
            db.session.add(user)
            db.session.commit()

            return "User registered correctly"

        except Exception as e:
            print(type(e))
            print(e.args)

            return "User with this login already exists or other error", 400


@app.route('/login', methods=['POST'])
def login():  # отрефактори все это плз читать невозможно))

    if request.method == "POST":

        json = request.get_json()
        curr_login = json["login"]
        curr_password = json["password"]

        curr_user_data = User.query \
            .filter_by(login=curr_login) \
            .first()

        if curr_user_data is None:
            return "User with this login is not exist", 400

        elif not check_password_hash(curr_user_data.password, curr_password):
            return "Incorrect password", 401

        else:
            curr_time = datetime.datetime.now()

            curr_user_valid_session = Session.query \
                .filter_by(user_id=curr_user_data.user_id) \
                .order_by(Session.expired.desc()) \
                .first()

            response = flask.Response()
            # Для видимости токена в Swagger Editor
            # Если у пользователя были сессии за последние сутки, то возвращаем токен данной сессии. В противном
            # случае создаем новый токен, новую сессию, заносим ее в бд.
            response.headers["Access-Control-Expose-Headers"] = "x-auth-key"
            
            if (curr_user_valid_session is not None) and (curr_user_valid_session.expired > curr_time):

                response.headers["x-auth-key"] = curr_user_valid_session.api_key

            else:

                curr_api_key_str = generate_api_key_by_time(curr_time)
                new_session = Session(
                    user_id=curr_user_data.user_id,
                    api_key=curr_api_key_str,
                    expired=datetime.datetime.now() + datetime.timedelta(days=1)
                )
                try:

                    db.session.add(new_session)
                    db.session.commit()

                except Exception as e:
                    print(type(e))
                    print(e.args)
                    return "Server internal error", 500  # exception mock

                response.headers["x-auth-key"] = curr_api_key_str

            response.data = "User was correctly login"

            return response


@app.route('/chats', methods=['GET', 'POST'])
def chats():
    curr_api_key = request.headers.get("x-auth-key")

    if is_api_key_working(curr_api_key):

        if request.method == "GET":

            all_chats = Chat.query.all()
            json_objects_list = []

            for curr_chat in all_chats:
                json_objects_list.append(
                    {
                        'chatId': curr_chat.chat_id,
                        'chatName': curr_chat.chat_name,
                        'creatorName': take_user_name_by_user_id(curr_chat.user_id)
                    })

            return jsonify(json_objects_list)

        elif request.method == "POST":

            json = request.get_json()
            curr_chat_name = json["chatName"]
            new_chat = Chat(
                user_id=take_user_id_by_api_key(curr_api_key),
                chat_name=curr_chat_name
            )
            try:
                db.session.add(new_chat)
                db.session.commit()
            except Exception as e:
                print(type(e))
                print(e.args)
                return "Server internal error", 500  # exception mock

            return "Chat was correctly created"

    else:
        return "Invalid api key", 400


@app.route('/chats/<int:chatID>', methods=['GET', 'POST'])
def messages_in_concrete_chat(chatID: int):
    curr_api_key = request.headers.get("x-auth-key")

    if take_chat_by_id(chatID) is None:
        return "Chat with this chatID is not exist", 400

    if is_api_key_working(curr_api_key):

        if request.method == "GET":

            all_messages_in_current_chat = Message.query.filter_by(chat_id=chatID).all()
            json_objects_list = []
            for curr_message in all_messages_in_current_chat:
                json_objects_list.append(
                    {'messageID': curr_message.message_id,
                     'creatorName': take_user_name_by_user_id(curr_message.user_id),
                     'timeStamp': curr_message.time_data,
                     "messageBody": curr_message.message_body
                     })

            return jsonify(json_objects_list)

        elif request.method == "POST":

            json = request.get_json()
            curr_message_body = json["messageBody"]
            curr_user_id = take_user_id_by_api_key(curr_api_key)
            new_message = Message(
                chat_id=chatID,
                user_id=curr_user_id,
                time_data=take_time_at_now_without_ms(),
                message_body=curr_message_body
            )

            try:
                db.session.add(new_message)
                db.session.commit()
            except Exception as e:
                print(type(e))
                print(e.args)
                return "Server internal error", 500  # exception mock

            return "Message was send correctly"

    else:
        return "Invalid api key", 400


@app.route('/chats/<int:chatID>/<int:lastMessageId>', methods=['GET'])
def all_messages_in_chat_after_message(chatID: int, lastMessageId: int):
    curr_api_key = request.headers.get("x-auth-key")

    if (take_chat_by_id(chatID) is None) \
            or (Message.query.filter_by(message_id=lastMessageId) is None):
        return "Chat with this chatID or message with lastMessageId is not exist", 400

    if is_api_key_working(curr_api_key):

        if request.method == "GET":

            all_messages_after_id = Message.query \
                .filter_by(chat_id=chatID) \
                .filter(Message.message_id > lastMessageId) \
                .order_by(Message.message_id).all()

            json_objects_list = []
            for curr_message in all_messages_after_id:
                json_objects_list.append(
                    {'messageID': curr_message.message_id,
                     'creatorName': take_user_name_by_user_id(curr_message.user_id),
                     'timeStamp': curr_message.time_data,
                     "messageBody": curr_message.message_body
                     })

            return jsonify(json_objects_list)

    else:
        return "Invalid api key", 400


# endregion


@app.route('/', methods=['GET'])
def test():
    response = flask.Response()
    response.data = "asdasd"
    return response

if __name__ == '__main__':
    db.create_all()
    app.run(host="localhost", port=5000, debug=True)
