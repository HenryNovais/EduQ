from flask import Blueprint, jsonify, request, current_app
from app.models.models import UserAnswer, Subject, User
from app import db
from sqlalchemy import func, case # <--- IMPORTANTE: Importar 'case'
import jwt

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/', methods=['GET'])
def get_stats():
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({"error": "Token ausente"}), 401
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = payload['user_id']
    except:
        return jsonify({"error": "Token inválido"}), 401

    # 1. Total de Questões Respondidas
    total_answered = UserAnswer.query.filter_by(user_id=user_id).count()

    # 2. Total de Acertos (CORREÇÃO PARA POSTGRESQL)
    # Em vez de func.sum(UserAnswer.is_correct), usamos:
    total_correct = db.session.query(func.count(UserAnswer.id)).filter_by(user_id=user_id, is_correct=True).scalar() or 0

    # 3. Estatísticas por Matéria (CORREÇÃO PARA POSTGRESQL)
    # Precisamos fazer um join para pegar o nome da matéria
    stats_by_subject = db.session.query(
        Subject.name,
        func.count(UserAnswer.id).label('total'),
        # O 'case' conta 1 se for true, senão null (que o count ignora)
        func.count(case((UserAnswer.is_correct == True, 1))).label('correct')
    ).join(UserAnswer.question)\
     .join(Question.topic)\
     .join(Topic.subject)\
     .filter(UserAnswer.user_id == user_id)\
     .group_by(Subject.name).all()
     
     # Nota: Se o seu modelo UserAnswer não tem relação direta, ajuste os joins acima
     # baseados em como você ligou as tabelas (UserAnswer -> Question -> Topic -> Subject)

    subject_data = []
    for subject_name, total, correct in stats_by_subject:
        subject_data.append({
            "name": subject_name,
            "total": total,
            "correct": correct,
            "percentage": round((correct / total) * 100, 1) if total > 0 else 0
        })

    return jsonify({
        "total_questions": total_answered,
        "correct_answers": total_correct,
        "incorrect_answers": total_answered - total_correct,
        "accuracy": round((total_correct / total_answered) * 100, 1) if total_answered > 0 else 0,
        "subjects": subject_data
    })