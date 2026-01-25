import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    
    # Tenta pegar a URL do Render
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and database_url.startswith("postgres://"):
        # Se achou URL do Render (PRODUÇÃO)
        SQLALCHEMY_DATABASE_URI = database_url.replace("postgres://", "postgresql://", 1)
    else:
        # Se NÃO achou (LOCAL / SUA MÁQUINA)
        # IMPORTANTE: Troque 'root' e '1234' pelo seu usuário e senha reais do MySQL
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost/vestibular_db'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False