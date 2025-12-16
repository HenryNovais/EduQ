import os

class Config:
    # Ajuste com seu usuário e senha do MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost/vestibular_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'sua_chave_secreta_super_segura'