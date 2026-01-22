# app/controllers/auth_controller.py
from app.services.auth_service import AuthService
from flask import Blueprint, request, jsonify, current_app
from app.models.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user = AuthService.register_user(data.get('name'), data.get('email'), data.get('password'))
    if user:
        return jsonify({"message": "User created"}), 201
    return jsonify({"error": "Email already exists"}), 400


@auth_bp.route('/update', methods=['PUT'])
def update_profile():
    # 1. Identificar Usuário
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token ausente"}), 401
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = payload['user_id']
    except:
        return jsonify({"error": "Token inválido"}), 401

    data = request.json
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # 2. Atualizar Nome (Livre)
    if 'name' in data and data['name']:
        user.name = data['name']
    
    # 3. Atualizar Senha (Com verificação da atual)
    if 'new_password' in data and data['new_password']:
        current_password = data.get('current_password')
        
        if not current_password:
            return jsonify({"error": "Para alterar a senha, informe a senha atual."}), 400
            
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({"error": "A senha atual está incorreta."}), 403
            
        user.password_hash = generate_password_hash(data['new_password'])

    db.session.commit()
    
    return jsonify({"message": "Perfil atualizado com sucesso!", "name": user.name}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    result = AuthService.login_user(data.get('email'), data.get('password'))
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Invalid credentials"}), 401