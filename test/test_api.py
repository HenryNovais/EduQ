import pytest
from app import create_app, db
from app.models.models import User, Institution, Subject, Topic, Question, Alternative

# --- CONFIGURAÇÃO (FIXTURES) ---
@pytest.fixture
def client():
    # Agora passamos a configuração DIRETO na criação do app
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', # Banco na memória RAM
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'chave_teste_123'
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all() # Cria as tabelas no SQLite (vazio)
            _populate_db_for_testing() # Popula o SQLite
            yield client
            db.session.remove()
            db.drop_all()


def _populate_db_for_testing():
    """Cria dados falsos (Seed) necessários para os testes rodarem."""
    # 1. Criar Domínios
    inst = Institution(name="ENEM")
    subj = Subject(name="Matemática")
    db.session.add(inst)
    db.session.add(subj)
    db.session.commit()

    topic = Topic(name="Álgebra", subject_id=subj.id)
    db.session.add(topic)
    db.session.commit()

    # 2. Criar uma Questão
    q = Question(
        statement="Quanto é 2 + 2?",
        explanation="A soma de 2 com 2 resulta em 4.",
        difficulty="EASY",
        institution_id=inst.id,
        topic_id=topic.id
    )
    db.session.add(q)
    db.session.commit()

    # 3. Criar Alternativas
    a1 = Alternative(text="3", is_correct=False, question_id=q.id)
    a2 = Alternative(text="4", is_correct=True, question_id=q.id) # ID provavelmente será 2
    db.session.add_all([a1, a2])
    db.session.commit()

# --- TESTES DE AUTENTICAÇÃO ---

def test_register(client):
    """Testa se consegue criar um usuário novo."""
    response = client.post('/api/auth/register', json={
        'name': 'Henry Teste',
        'email': 'teste@eduq.com',
        'password': '123'
    })
    assert response.status_code == 201

def test_login(client):
    """Testa o fluxo de login e recebimento do Token."""
    # Primeiro registra
    client.post('/api/auth/register', json={
        'name': 'Henry Teste',
        'email': 'teste@eduq.com',
        'password': '123'
    })
    
    # Tenta logar
    response = client.post('/api/auth/login', json={
        'email': 'teste@eduq.com',
        'password': '123'
    })
    
    data = response.get_json()
    assert response.status_code == 200
    assert 'token' in data
    assert data['name'] == 'Henry Teste'
    return data['token']

# --- TESTES DE QUESTÕES ---

def test_get_filter_options(client):
    """Testa se a rota /options retorna as instituições e matérias cadastradas."""
    response = client.get('/api/questions/options')
    data = response.get_json()
    
    assert response.status_code == 200
    assert "ENEM" in data['institutions']
    assert "Matemática" in data['subjects']

def test_search_questions(client):
    """Testa a busca de questões com filtros."""
    # Busca sem filtro
    response = client.get('/api/questions/search')
    data = response.get_json()
    assert len(data) >= 1
    assert data[0]['institution'] == "ENEM"
    
    # Busca com filtro de dificuldade
    response_filter = client.get('/api/questions/search?difficulty=EASY')
    assert len(response_filter.get_json()) == 1

def test_answer_question_flow(client):
    """Testa o ciclo completo: Logar -> Responder Certo -> Verificar Stats."""
    
    # 1. Login para pegar o Token
    token = test_login(client)
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Responder a Questão (ID 1)
    # Pegamos a alternativa correta (que sabemos que é a segunda, ID 2, no seed)
    q_id = 1
    alt_id_correta = 2 

    response = client.post(f'/api/questions/check/{q_id}', json={
        'alternative_id': alt_id_correta
    }, headers=headers)

    data = response.get_json()
    assert response.status_code == 200
    assert data['correct'] is True
    assert "A soma de 2 com 2" in data['explanation']

    # 3. Verificar se contou no Dashboard (Stats)
    stats_response = client.get('/api/stats/dashboard', headers=headers)
    stats = stats_response.get_json()
    
    assert stats['total_questions'] == 1
    assert stats['correct_count'] == 1
    # Verifica se Matemática apareceu nos stats
    assert stats['subjects'][0]['name'] == 'Matemática'