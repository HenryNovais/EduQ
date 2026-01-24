from app.models.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app

class AuthService:
    @staticmethod
    def register_user(name, email, password):
        if User.query.filter_by(email=email).first():
            return None # Usuário já existe
        
        hashed_pw = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            token = jwt.encode({
                'user_id': user.id,
                'is_admin': user.is_admin,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")
            return {'token': token, 
                    'name': user.name, 
                    'email': user.email,
                    'is_admin': user.is_admin
                    }
        return None