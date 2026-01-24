import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'

    # Pega a URL do banco do Render. Se não tiver, usa o SQLite local (para testes)
    database_url = os.environ.get('DATABASE_URL')

    if database_url and database_url.startswith("postgres://"):
        # MUNDO DO RENDER (Produção)
        SQLALCHEMY_DATABASE_URI = database_url.replace("postgres://", "postgresql://", 1)
    else:
        # MUNDO LOCAL (Sua Máquina) - Coloque aqui sua conexão MySQL antiga!
        # Exemplo: mysql+pymysql://root:sua_senha@localhost/vestibular_db
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost/vestibular_db'

    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False