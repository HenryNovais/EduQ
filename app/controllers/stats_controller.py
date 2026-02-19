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
        # 2. Estatísticas Gerais (Compatível com MySQL e Postgres)
        total_answered = UserAnswer.query.filter_by(user_id=user_id).count()
        
        # Filtro explícito para contar acertos
        total_correct = UserAnswer.query.filter_by(user_id=user_id, is_correct=True).count()
        
        total_incorrect = total_answered - total_correct
        accuracy = round((total_correct / total_answered) * 100, 1) if total_answered > 0 else 0

        # 3. Estatísticas por Matéria
        # Usamos OUTER JOIN para não quebrar se faltar tópico/matéria
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

        # 4. Processamento para o Frontend (Restaurando a lógica antiga)
        subjects_performance = []
        for name, total, correct in stats_query:
            # Garante que correct não seja None
            safe_correct = correct or 0
            
            # Calcula porcentagem inteira para usar na lógica de força/fraqueza
            score = round((safe_correct / total) * 100) if total > 0 else 0
            
            # Lógica de "Pontos Fortes" (> 60%) vs "Áreas de Melhoria"
            status_type = 'strength' if score >= 60 else 'weakness'
            
            subjects_performance.append({
                'name': name,
                'score': score,      # Frontend espera 'score'
                'type': status_type  # Frontend espera 'type' para saber onde exibir
            })

        # Ordenar: Maior pontuação primeiro
        subjects_performance.sort(key=lambda x: x['score'], reverse=True)

        # 5. Retorno com as chaves EXATAS que o script.js espera
        return jsonify({
            'total_questions': total_answered,
            'accuracy': accuracy,
            'correct_count': total_correct,     
            'incorrect_count': total_incorrect, 
            'subjects': subjects_performance
        })

    except Exception as e:
        print(f"ERRO CRÍTICO STATS: {e}") 
        return jsonify({"error": str(e)}), 500
