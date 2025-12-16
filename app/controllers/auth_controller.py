# app/controllers/auth_controller.py
from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user = AuthService.register_user(data.get('name'), data.get('email'), data.get('password'))
    if user:
        return jsonify({"message": "User created"}), 201
    return jsonify({"error": "Email already exists"}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    result = AuthService.login_user(data.get('email'), data.get('password'))
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Invalid credentials"}), 401