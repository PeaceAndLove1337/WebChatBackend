import datetime

import flask
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from data.allfunc import take_user_by_login, take_last_user_session_by_user, \
    add_new_session_in_db, add_new_user_in_db, is_api_key_working, take_all_chats, take_user_name_by_user_id, \
    add_new_chat_in_db, take_chat_by_id, take_last_messages_in_chat, add_new_message_in_chat_in_db, \
    take_message_by_message_id, take_messages_in_chat_after_message_id, take_messages_in_chat_before_message_id

main_routes = Blueprint("main_routes", __name__)


@main_routes.route('/register', methods=['POST'])
def register():
    if request.method == "POST":

        json = request.get_json()
        curr_login = json["login"]
        curr_password = json["password"]
        if add_new_user_in_db(curr_login, curr_password):
            return "User registered correctly", 200
        else:
            return "Bad request: User with this login already exists or other error", 400


@main_routes.route('/login', methods=['POST'])
def login():
    if request.method == "POST":

        json = request.get_json()
        curr_login = json["login"]
        curr_password = json["password"]

        curr_user_data = take_user_by_login(curr_login)

        if curr_user_data is None:
            return "Bad request: User with this login is not exist", 400

        elif not check_password_hash(curr_user_data.password, curr_password):
            return "Unauthorized: Incorrect password", 401

        else:
            curr_time = datetime.datetime.now()

            curr_user_valid_session = take_last_user_session_by_user(curr_user_data)

            response = flask.Response()
            # Если у пользователя были сессии за последние сутки, то возвращаем токен данной сессии. В противном
            # случае создаем новый токен, новую сессию, заносим ее в бд.
            response.headers["Access-Control-Expose-Headers"] = "x-auth-key"

            if (curr_user_valid_session is not None) and (curr_user_valid_session.expired_date > curr_time):

                response.headers["x-auth-key"] = curr_user_valid_session.api_key

            else:
                api_key = add_new_session_in_db(curr_user_data)

                if api_key is not None:
                    response.headers["x-auth-key"] = api_key
                    response.data = "User was correctly login", 200
                else:
                    response.data = "Internal Server Error", 500

            return response


@main_routes.route('/chats', methods=['GET', 'POST'])
def chats():
    curr_api_key = request.headers.get("x-auth-key")

    if is_api_key_working(curr_api_key):

        if request.method == "GET":

            all_chats = take_all_chats()
            json_objects_list = []

            for curr_chat in all_chats:
                json_objects_list.append(
                    {
                        'chatId': curr_chat.chat_id,
                        'chatName': curr_chat.chat_name,
                        'creatorName': take_user_name_by_user_id(curr_chat.user_id)
                    })
            return jsonify(json_objects_list), 200

        elif request.method == "POST":

            json = request.get_json()
            curr_chat_name = json["chatName"]
            if add_new_chat_in_db(curr_api_key, curr_chat_name):
                return "Chat was created correctly", 200
            else:
                return "Internal Server Error", 500

    else:
        return "Unauthorized: Invalid api key", 401


# todo Задумка следующая: в качестве параметров передается count - количество сообщений до или после
#  сообщения с заданным ID (Соответственно, если count>0, то берутся сообщения после, если <0, то сообщения до
@main_routes.route('/chats/<int:chat_id>', methods=['GET', 'POST'])
def messages_in_concrete_chat(chat_id: int):
    curr_api_key = request.headers.get("x-auth-key")

    if take_chat_by_id(chat_id) is None:
        return "Bad Request: Chat with this chat_id is not exist", 400

    if is_api_key_working(curr_api_key):

        if request.method == "GET":

            count = request.args.get('count', default=100, type=int)
            if count == 0:
                count = 100
            message_id = request.args.get('message_id', default=None, type=int)

            if take_message_by_message_id(message_id) is None:
                return "Bad Request: Message with this message_id is not exist", 400

            if message_id is None:

                messages = take_last_messages_in_chat(chat_id, count)
                json_objects_list = []
                for curr_message in messages:
                    json_objects_list.append(
                        {'messageID': curr_message.message_id,
                         'creatorName': take_user_name_by_user_id(curr_message.user_id),
                         'timeStamp': curr_message.time_data,
                         "messageBody": curr_message.message_body
                         })

                return jsonify(json_objects_list), 200

            else:
                if count > 0:
                    messages_after = take_messages_in_chat_after_message_id(chat_id, message_id, count)
                    json_objects_list = []
                    for curr_message in messages_after:
                        json_objects_list.append(
                            {'messageID': curr_message.message_id,
                             'creatorName': take_user_name_by_user_id(curr_message.user_id),
                             'timeStamp': curr_message.time_data,
                             "messageBody": curr_message.message_body
                             })

                    return jsonify(json_objects_list), 200

                else:
                    messages_before = take_messages_in_chat_before_message_id(chat_id, message_id, -count)
                    json_objects_list = []
                    for curr_message in messages_before:
                        json_objects_list.append(
                            {'messageID': curr_message.message_id,
                             'creatorName': take_user_name_by_user_id(curr_message.user_id),
                             'timeStamp': curr_message.time_data,
                             "messageBody": curr_message.message_body
                             })

                    return jsonify(json_objects_list), 200

        elif request.method == "POST":

            json = request.get_json()
            curr_message_body = json["messageBody"]
            if add_new_message_in_chat_in_db(curr_api_key, chat_id, curr_message_body):
                return "Message was send correctly", 200
            else:
                return "Internal Server Error", 500

    else:
        return "Unauthorized: Invalid api key", 401


@main_routes.route('/test', methods=['GET'])
def test():
    one = request.args.get('arg1', default="SOME_ARGUMENT", type=str)
    two = request.args.get('arg2', default=22, type=int)
    return "Backend works correctly  " + one + "  " + str(two)
