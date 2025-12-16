from flask import Blueprint, jsonify, request
from app.models.models import Question, User, Alternative  # Supondo que você tenha mapeado UserAnswers
from app import db
from sqlalchemy import func, text

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    # Aqui você pegaria o ID do usuário pelo Token JWT (simplificado para exemplo)
    # user_id = get_jwt_identity() 
    user_id = 1 # ID fixo para teste, mude para dinâmico depois

    # SQL Puro para agilidade nas estatísticas (pode usar ORM também)
    sql_total = text("SELECT COUNT(*) FROM user_answers WHERE user_id = :uid")
    sql_correct = text("SELECT COUNT(*) FROM user_answers WHERE user_id = :uid AND is_correct = 1")
    
    total = db.session.execute(sql_total, {'uid': user_id}).scalar() or 0
    correct = db.session.execute(sql_correct, {'uid': user_id}).scalar() or 0
    incorrect = total - correct
    accuracy = round((correct / total * 100), 1) if total > 0 else 0

    # Matérias (Mockado para exemplo, ideal é fazer GROUP BY subject no SQL)
    subjects_performance = [
        {'name': 'Matemática', 'score': 85, 'type': 'strength'},
        {'name': 'Física', 'score': 78, 'type': 'strength'},
        {'name': 'História', 'score': 58, 'type': 'weakness'},
        {'name': 'Geografia', 'score': 62, 'type': 'weakness'}
    ]

    return jsonify({
        'total_questions': total,
        'accuracy': accuracy,
        'correct_count': correct,
        'incorrect_count': incorrect,
        'subjects': subjects_performance
    })