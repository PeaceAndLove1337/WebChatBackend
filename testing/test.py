import unittest

from application.data.db_models import db
from application.data.db_queries import take_user_by_login
from application.main import app
from application.routes.routes import main_routes


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:///Projects///StudentProjects///' \
                                                'MobileNetworksSystems///WebChatApp///WebChatBackend///' \
                                                'testing///data///test_webchat.db'
        self.app = app.test_client()
        db.init_app(app)
        app.register_blueprint(main_routes)
        with app.app_context():
            db.create_all()

    def tearDown(self):
        db.session.remove()
        with app.app_context():
            db.drop_all()

    def test_api_available(self):
        rv = self.app.get('/test?arg1=Hello')
        assert 'Backend works correctly  Hello  0'.encode() == rv.data

    def test_register(self):
        user_login = 'SomeUser'
        response = self.app.post('/register',
                                 json={'login': user_login, 'password': 'MyAweSomePassWd213'},
                                 content_type='application/json')
        with app.app_context():
            is_user_exist = False if take_user_by_login(user_login) is None else True
            assert is_user_exist
        assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()
