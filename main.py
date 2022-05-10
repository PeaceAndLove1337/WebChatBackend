from flask import Flask
from flask_cors import CORS

from application.data.db_models import db
from application.routes.routes import main_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///application///data///webchat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, resources={r'/*': {'origins': '*'}})


if __name__ == '__main__':
    db.init_app(app)
    db.app = app
    db.create_all()
    app.register_blueprint(main_routes)
    app.run(host="0.0.0.0", port=8080, debug=True)
