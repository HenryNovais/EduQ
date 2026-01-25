from flask import Blueprint, jsonify, request, current_app
from app.models.models import UserAnswer, Question, Topic, Subject
from app import db
from sqlalchemy import func, case
import jwt

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/dashboard', methods=['GET']) 
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
        # 2. Números Totais (Isso aqui TEM que funcionar se estiver salvando)
        total_answered = UserAnswer.query.filter_by(user_id=user_id).count()
        
        # Contagem de acertos compatível com Postgres
        total_correct = UserAnswer.query.filter_by(user_id=user_id, is_correct=True).count()
        
        accuracy = round((total_correct / total_answered) * 100, 1) if total_answered > 0 else 0

        # 3. Estatísticas por Matéria (Agora com OUTER JOIN para não sumir dados)
        # Se a matéria for Null, substituímos o nome por "Geral/Outros"
        stats_query = db.session.query(
            func.coalesce(Subject.name, 'Geral').label('subject_name'),
            func.count(UserAnswer.id).label('total'),
            func.count(case((UserAnswer.is_correct == True, 1))).label('correct')
        ).select_from(UserAnswer)\
         .outerjoin(Question, UserAnswer.question_id == Question.id)\
         .outerjoin(Topic, Question.topic_id == Topic.id)\
         .outerjoin(Subject, Topic.subject_id == Subject.id)\
         .filter(UserAnswer.user_id == user_id)\
         .group_by(func.coalesce(Subject.name, 'Geral')).all()

        subject_data = []
        for name, total, correct in stats_query:
            subject_data.append({
                "name": name,
                "total": total,
                "correct": correct,
                "percentage": round(((correct or 0) / total) * 100, 1) if total > 0 else 0
            })

        # DEBUG: Adicionei esse campo para você ver se o Backend está achando algo
        return jsonify({
            "debug_info": f"Usuário {user_id} tem {total_answered} respostas no banco.",
            "total_questions": total_answered,
            "correct_answers": total_correct,
            "incorrect_answers": total_answered - total_correct,
            "accuracy": accuracy,
            "subjects": subject_data
        })

    except Exception as e:
        print(f"ERRO CRÍTICO STATS: {e}") 
        return jsonify({"error": str(e)}), 500