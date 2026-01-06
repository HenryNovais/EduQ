from flask import Blueprint, jsonify, request, current_app
from app.repositories.question_repository import QuestionRepository
from app.models.models import UserAnswer, Alternative
from app import db
import jwt

question_bp = Blueprint('questions', __name__)

@question_bp.route('/search', methods=['GET'])
def search():
    filters = {
        'difficulty': request.args.get('difficulty'),
        # Você pode adicionar os outros filtros aqui depois (materia, assunto)
    }
    questions = QuestionRepository.get_all_filtered(filters)
    
    output = []
    for q in questions:
        alts = [{'id': a.id, 'text': a.text} for a in q.alternatives]
        output.append({
            'id': q.id,
            'statement': q.statement,
            'explanation': q.explanation,
            'difficulty': q.difficulty,
            'alternatives': alts
        })
    return jsonify(output), 200

@question_bp.route('/check/<int:question_id>', methods=['POST'])
def check_answer(question_id):
    data = request.json
    alt_id = data.get('alternative_id')
    
    # 1. Identificar o Usuário pelo Token
    auth_header = request.headers.get('Authorization')
    user_id = 1 # Fallback caso não tenha token (para testes)
    
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = payload['user_id']
        except:
            return jsonify({"error": "Token inválido"}), 401

    # 2. Verificar a Resposta
    question = QuestionRepository.get_by_id(question_id)
    correct_alt = next((a for a in question.alternatives if a.is_correct), None)
    
    if not correct_alt:
        return jsonify({"error": "Questão sem resposta cadastrada"}), 500

    is_correct = (correct_alt.id == alt_id)

    # 3. SALVAR NO BANCO DE DADOS (A CORREÇÃO É AQUI)
    # Verifica se já respondeu essa questão antes para não duplicar infinitamente (opcional)
    # Se quiser permitir múltiplas tentativas, remova este bloco 'previous_answer'
    previous_answer = UserAnswer.query.filter_by(user_id=user_id, question_id=question_id).first()
    
    if previous_answer:
        # Atualiza a resposta existente
        previous_answer.alternative_id = alt_id
        previous_answer.is_correct = is_correct
    else:
        # Cria um novo registro
        new_answer = UserAnswer(
            user_id=user_id,
            question_id=question_id,
            alternative_id=alt_id,
            is_correct=is_correct
        )
        db.session.add(new_answer)
    
    db.session.commit() # Salva efetivamente no banco

    # 4. Retorna o resultado
    return jsonify({
        "correct": is_correct,
        "correct_id": correct_alt.id,
        "explanation": question.explanation
    })