
from flask import Flask, request, jsonify
from flask_cors import CORS

from allfunc import db
from routes import main_blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webchat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, resources={r'/*': {'origins': '*'}})


if __name__ == '__main__':
    db.init_app(app)
    db.app = app
    db.create_all()
    app.register_blueprint(main_blueprint)
    app.run(host="localhost", port=5000, debug=True)
