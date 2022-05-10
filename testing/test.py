import unittest

from flask_sqlalchemy import SQLAlchemy

from application.main import app

db = SQLAlchemy()


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:///Projects///StudentProjects///' \
                                                'MobileNetworksSystems///WebChatApp///WebChatBackend///' \
                                                'testing///data///test_webchat.db'
        self.app = app.test_client()
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def tearDown(self):
        db.session.remove()
        with app.app_context():
            db.drop_all()

    def test1(self):
        assert 5 == (2+3)


if __name__ == '__main__':
    unittest.main()
