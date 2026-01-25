import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    
    # 1. Tenta pegar a URL do Render
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # SE TEM URL NO AMBIENTE (RENDER), USA ELA
        # Correção para o SQLAlchemy (ele precisa que comece com postgresql://)
        if database_url.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URI = database_url.replace("postgres://", "postgresql://", 1)
        else:
            SQLALCHEMY_DATABASE_URI = database_url
    else:
        # SE NÃO TEM (SEU COMPUTADOR), USA O MYSQL
        # Substitua root:1234 pela sua senha real se precisar
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost/vestibular_db'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False