import pytest
from clinic_connect import create_app
from clinic_connect.database import db
from clinic_connect.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False # Disable CSRF token checks during unit tests

@pytest.fixture
def app():
    # Instantiate app with test configs
    app = create_app(TestConfig)
    
    with app.app_context():
        # Setup tables in memory
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def session_setup(client):
    """Sets up a mock clinic session in the client context"""
    with client.session_transaction() as sess:
        sess['clinic_id'] = 1
        sess['clinic_name'] = 'Test Clinic'
        sess['active_role'] = 'receptionist'
        sess['network_status'] = 'online'
    return client
