from flask import Flask
from flask_cors import CORS

from data.allfunc import db
from routes.routes import main_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data///webchat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, resources={r'/*': {'origins': '*'}})


if __name__ == '__main__':
    db.init_app(app)
    db.app = app
    db.create_all()
    app.register_blueprint(main_routes)
    app.run(host="localhost", port=5000, debug=True)
