import pytest
from app import create_app, db
from app.models.models import User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # BD em memória para teste
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_register_and_login(client):
    # Teste Registro
    res = client.post('/api/auth/register', json={
        'name': 'Henry Teste',
        'email': 'henry@test.com',
        'password': '123'
    })
    assert res.status_code == 201

    # Teste Login
    res = client.post('/api/auth/login', json={
        'email': 'henry@test.com',
        'password': '123'
    })
    assert res.status_code == 200
    assert 'token' in res.json

def test_invalid_login(client):
    res = client.post('/api/auth/login', json={
        'email': 'fake@email.com',
        'password': '000'
    })
    assert res.status_code == 401