from flask import Blueprint, jsonify, request, current_app
from app.models.models import UserAnswer, Question, Topic, Subject, User
from app import db
from sqlalchemy import func, case
import jwt

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/', methods=['GET'])
def get_stats():
    # 1. Autenticação
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({"error": "Token ausente"}), 401
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = payload['user_id']
    except:
        return jsonify({"error": "Token inválido"}), 401

    try:
        # 2. Estatísticas Gerais (Abordagem compatível com Postgres e MySQL)
        total_answered = UserAnswer.query.filter_by(user_id=user_id).count()
        total_correct = UserAnswer.query.filter_by(user_id=user_id, is_correct=True).count()
        
        # Evita divisão por zero
        accuracy = round((total_correct / total_answered) * 100, 1) if total_answered > 0 else 0

        # 3. Estatísticas por Matéria
        # Query complexa: Junta Resposta -> Questão -> Tópico -> Matéria
        stats_query = db.session.query(
            Subject.name,
            func.count(UserAnswer.id).label('total'),
            func.count(case((UserAnswer.is_correct == True, 1))).label('correct')
        ).join(Question, UserAnswer.question_id == Question.id)\
         .join(Topic, Question.topic_id == Topic.id)\
         .join(Subject, Topic.subject_id == Subject.id)\
         .filter(UserAnswer.user_id == user_id)\
         .group_by(Subject.name).all()

        subject_data = []
        for name, total, correct in stats_query:
            subject_data.append({
                "name": name,
                "total": total,
                "correct": correct,
                "percentage": round((correct / total) * 100, 1) if total > 0 else 0
            })

        return jsonify({
            "total_questions": total_answered,
            "correct_answers": total_correct,
            "incorrect_answers": total_answered - total_correct,
            "accuracy": accuracy,
            "subjects": subject_data
        })

    except Exception as e:
        print(f"ERRO STATS: {e}") # Debug no terminal do Render
        return jsonify({"error": "Erro ao calcular estatísticas"}), 500