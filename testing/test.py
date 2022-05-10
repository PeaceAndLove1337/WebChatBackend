import unittest

from application.data.db_models import db
from application.data.db_queries import take_user_by_login, take_last_user_session_by_user
from main import app
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
        expected_result = 'Backend works correctly  Hello  0'.encode()
        assert expected_result == rv.data

    def test_register(self):
        user_login = 'SomeUser'
        user_password = 'MyAweSomePassWd213'
        response = self.register_new_user(user_login, user_password)
        with app.app_context():
            is_user_exist = False if take_user_by_login(user_login) is None else True
            assert is_user_exist
        assert response.status_code == 200

    def test_login(self):
        user_login = 'SomeUser'
        user_password = 'MyAweSomePassWd213'
        self.register_new_user(user_login, user_password)
        response = self.app.post('/login',
                                 json={'login': user_login, 'password': user_password},
                                 content_type='application/json')
        with app.app_context():
            last_api_key = take_last_user_session_by_user(take_user_by_login(user_login)).api_key
            assert last_api_key == response.headers["x-auth-key"]
        assert response.status_code == 200

    def register_new_user(self, user_login, user_password):
        return self.app.post('/register',
                             json={'login': user_login, 'password': user_password},
                             content_type='application/json')


if __name__ == '__main__':
    unittest.main()
