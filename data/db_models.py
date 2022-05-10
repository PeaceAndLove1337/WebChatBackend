from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
    chat_id = db.Column(db.Integer, db.ForeignKey("Chats.chat_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=False)
    time_data = db.Column(db.String, nullable=False)
    message_body = db.Column(db.String(400), nullable=False)

    def __repr__(self):
        return '<Message %r' % self.session_id
