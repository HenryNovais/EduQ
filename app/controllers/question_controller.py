from flask import Blueprint, jsonify, request, current_app
from app.repositories.question_repository import QuestionRepository
from app.models.models import UserAnswer, Alternative
from app import db
import jwt

question_bp = Blueprint('questions', __name__)

# Rota nova para preencher os filtros do HTML
@question_bp.route('/options', methods=['GET'])
def get_options():
    options = QuestionRepository.get_filter_options()
    return jsonify(options), 200

@question_bp.route('/search', methods=['GET'])
def search():
    # Captura todos os filtros da URL
    filters = {
        'difficulty': request.args.get('difficulty'),
        'institution': request.args.get('institution'),
        'subject': request.args.get('subject'),
        'topic': request.args.get('topic')
    }
    
    questions = QuestionRepository.get_all_filtered(filters)
    
    output = []
    for q in questions:
        alts = [{'id': a.id, 'text': a.text} for a in q.alternatives]
        
        # AQUI ESTAVA O ERRO DAS TAGS:
        # Agora pegamos o nome real do relacionamento no banco
        inst_name = q.institution.name if q.institution else "Outra"
        topic_name = q.topic.name if q.topic else "Geral"
        # Navegamos de Questão -> Tópico -> Matéria
        subject_name = q.topic.subject.name if (q.topic and q.topic.subject) else "Geral"

        output.append({
            'id': q.id,
            'statement': q.statement,
            'explanation': q.explanation,
            'difficulty': q.difficulty,
            'institution': inst_name,  # Manda o nome certo pro frontend
            'subject': subject_name,   # Manda o nome certo pro frontend
            'topic': topic_name,       # Manda o nome certo pro frontend
            'alternatives': alts
        })
    return jsonify(output), 200

@question_bp.route('/check/<int:question_id>', methods=['POST'])
def check_answer(question_id):
    data = request.json
    alt_id = data.get('alternative_id')
    auth_header = request.headers.get('Authorization')
    user_id = 1 
    
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = payload['user_id']
        except:
            pass

    question = QuestionRepository.get_by_id(question_id)
    correct_alt = next((a for a in question.alternatives if a.is_correct), None)
    
    if not correct_alt:
        return jsonify({"error": "Questão sem resposta"}), 500

    is_correct = (correct_alt.id == alt_id)

    previous_answer = UserAnswer.query.filter_by(user_id=user_id, question_id=question_id).first()
    if previous_answer:
        previous_answer.alternative_id = alt_id
        previous_answer.is_correct = is_correct
    else:
        new_answer = UserAnswer(user_id=user_id, question_id=question_id, alternative_id=alt_id, is_correct=is_correct)
        db.session.add(new_answer)
    
    db.session.commit()

    return jsonify({
        "correct": is_correct,
        "correct_id": correct_alt.id,
        "explanation": question.explanation
    })