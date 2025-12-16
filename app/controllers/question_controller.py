# app/controllers/question_controller.py
from flask import Blueprint, jsonify, request
from app.repositories.question_repository import QuestionRepository

question_bp = Blueprint('questions', __name__)

@question_bp.route('/search', methods=['GET'])
def search():
    filters = {
        'difficulty': request.args.get('difficulty'),
        # Capturar outros filtros
    }
    questions = QuestionRepository.get_all_filtered(filters)
    
    # Serialização manual (ou usar Marshmallow)
    output = []
    for q in questions:
        alts = [{'id': a.id, 'text': a.text} for a in q.alternatives]
        output.append({
            'id': q.id,
            'statement': q.statement,
            'explanation': q.explanation, # Importante para o feedback
            'difficulty': q.difficulty,
            'alternatives': alts
        })
    return jsonify(output), 200

@question_bp.route('/check/<int:question_id>', methods=['POST'])
def check_answer(question_id):
    # Lógica para verificar se a alternativa escolhida é a correta
    # Retorna {correct: true/false, explanation: "..."}
    data = request.json
    alt_id = data.get('alternative_id')
    question = QuestionRepository.get_by_id(question_id)
    
    correct_alt = next((a for a in question.alternatives if a.is_correct), None)
    
    is_correct = (correct_alt.id == alt_id)
    return jsonify({
        "correct": is_correct,
        "correct_id": correct_alt.id,
        "explanation": question.explanation
    })