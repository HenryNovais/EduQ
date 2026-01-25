from flask import Blueprint, jsonify, request, current_app
from app import db
from sqlalchemy import text
import jwt

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    # 1. Identificar o usuário pelo Token (igual fizemos no question_controller)
    auth_header = request.headers.get('Authorization')
    user_id = 1 # ID padrão para testes caso não tenha token
    
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = payload['user_id']
        except:
            return jsonify({"error": "Token inválido"}), 401

    # 2. Estatísticas Gerais (Total, Acertos, Erros)
    sql_total = text("SELECT COUNT(*) FROM user_answers WHERE user_id = :uid")
    sql_correct = text("SELECT COUNT(*) FROM user_answers WHERE user_id = :uid AND is_correct = 1")
    
    total = db.session.execute(sql_total, {'uid': user_id}).scalar() or 0
    correct = db.session.execute(sql_correct, {'uid': user_id}).scalar() or 0
    incorrect = total - correct
    accuracy = round((correct / total * 100), 1) if total > 0 else 0

    # 3. Estatísticas por Matéria (AQUI ESTÁ A MÁGICA ✨)
    # Fazemos um JOIN entre Resposta -> Questão -> Tópico -> Matéria
    sql_subjects = text("""
        SELECT 
            s.name AS subject_name,
            COUNT(ua.id) as total_answered,
            SUM(CASE WHEN ua.is_correct = 1 THEN 1 ELSE 0 END) as total_correct
        FROM user_answers ua
        JOIN questions q ON ua.question_id = q.id
        JOIN topics t ON q.topic_id = t.id
        JOIN subjects s ON t.subject_id = s.id
        WHERE ua.user_id = :uid
        GROUP BY s.name
    """)
    
    results = db.session.execute(sql_subjects, {'uid': user_id}).fetchall()
    
    subjects_performance = []
    
    for row in results:
        # O SQLAlchemy retorna as colunas na ordem ou por nome dependendo da versão
        # Vamos garantir o cálculo da porcentagem
        subj_total = row.total_answered
        subj_correct = row.total_correct
        subj_acc = (subj_correct / subj_total * 100) if subj_total > 0 else 0
        
        # Regra de Negócio:
        # Se acertou 60% ou mais = Ponto Forte (strength)
        # Menos de 60% = Precisa Melhorar (weakness)
        status_type = 'strength' if subj_acc >= 60 else 'weakness'
        
        subjects_performance.append({
            'name': row.subject_name,
            'score': round(subj_acc),
            'type': status_type
        })

    # Ordenar: Primeiro os maiores percentuais para ficar bonito na tela
    subjects_performance.sort(key=lambda x: x['score'], reverse=True)

    return jsonify({
        'total_questions': total,
        'accuracy': accuracy,
        'correct_count': correct,
        'incorrect_count': incorrect,
        'subjects': subjects_performance
    })