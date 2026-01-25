from flask import Blueprint, jsonify, request, current_app
from app.repositories.question_repository import QuestionRepository
from app.models.models import UserAnswer, Alternative
from app import db
import jwt
from datetime import datetime
from app.models.models import Institution, Subject, Topic, Question, Alternative, UserAnswer, User # Adicione os imports

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
    
    # 1. AUTENTICAÇÃO: Descobre quem é o usuário
    user_id = 1 # Fallback para testes
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = payload['user_id']
        except:
            return jsonify({"error": "Token inválido"}), 401

    # 2. CÁLCULO: Verifica se acertou (Isso tem que vir ANTES de salvar)
    question = QuestionRepository.get_by_id(question_id)
    if not question:
        return jsonify({"error": "Questão não encontrada"}), 404

    correct_alt = next((a for a in question.alternatives if a.is_correct), None)
    if not correct_alt:
        return jsonify({"error": "Questão sem resposta cadastrada"}), 500

    is_correct = (correct_alt.id == alt_id)

    # 3. BANCO DE DADOS: Salva ou Atualiza a resposta (Com Debug)
    try:
        print(f"DEBUG: Tentando salvar - User: {user_id}, Questão: {question_id}, Acertou: {is_correct}")

        previous_answer = UserAnswer.query.filter_by(user_id=user_id, question_id=question_id).first()
        
        if previous_answer:
            # Atualiza se já respondeu antes
            previous_answer.alternative_id = alt_id
            previous_answer.is_correct = is_correct
        else:
            # Cria novo registro se é a primeira vez
            new_answer = UserAnswer(
                user_id=user_id,
                question_id=question_id,
                alternative_id=alt_id, # Cuidado: sua variável chama alt_id, não alternative_id
                is_correct=is_correct
            )
            db.session.add(new_answer)
        
        db.session.commit()
        print("✅ Resposta salva com sucesso no banco!")

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERRO AO SALVAR NO BANCO: {e}")
        # Mesmo se der erro no banco, vamos retornar a correção pro usuário não ficar travado
        # return jsonify({"error": str(e)}), 500

    # 4. RETORNO PARA O FRONTEND
    return jsonify({
        "correct": is_correct,
        "correct_id": correct_alt.id,
        "explanation": question.explanation
    })


@question_bp.route('/create', methods=['POST'])
def create_question():
    # 1. Verificação de Segurança (Apenas Admin)
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({"error": "Não autorizado"}), 401
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        if not payload.get('is_admin'):
            return jsonify({"error": "Acesso restrito a administradores"}), 403
    except:
        return jsonify({"error": "Token inválido"}), 401

    data = request.json

    try:
        # 2. Processar Instituição (Busca ou Cria)
        inst_name = data.get('institution')
        institution = Institution.query.filter_by(name=inst_name).first()
        if not institution:
            institution = Institution(name=inst_name)
            db.session.add(institution)
            db.session.flush() # Gera o ID sem commitar ainda

        # 3. Processar Matéria (Busca ou Cria)
        subj_name = data.get('subject')
        subject = Subject.query.filter_by(name=subj_name).first()
        if not subject:
            subject = Subject(name=subj_name)
            db.session.add(subject)
            db.session.flush()

        # 4. Processar Assunto/Tópico (Busca ou Cria, ligado à Matéria)
        topic_name = data.get('topic')
        topic = Topic.query.filter_by(name=topic_name, subject_id=subject.id).first()
        if not topic:
            topic = Topic(name=topic_name, subject=subject) # Associa à matéria acima
            db.session.add(topic)
            db.session.flush()

        # 5. Criar a Questão
        new_q = Question(
            statement=data.get('statement'),
            explanation=data.get('explanation'),
            difficulty=data.get('difficulty'),
            institution=institution,
            topic=topic,
            year=datetime.now().year # Ou pegar do input se quiser
        )
        db.session.add(new_q)
        db.session.flush()

        # 6. Criar Alternativas
        alternatives_data = data.get('alternatives') # Lista de objetos {text: "...", is_correct: bool}
        for alt in alternatives_data:
            new_alt = Alternative(
                text=alt['text'],
                is_correct=alt['is_correct'],
                question=new_q
            )
            db.session.add(new_alt)

        db.session.commit()
        return jsonify({"message": "Questão cadastrada com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@question_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete_question(id):
    # 1. Verificação de Segurança (Admin)
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({"error": "Token ausente"}), 401
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        if not payload.get('is_admin'):
            return jsonify({"error": "Acesso negado. Apenas admins."}), 403
    except:
        return jsonify({"error": "Token inválido"}), 401

    # 2. Buscar a questão
    question = QuestionRepository.get_by_id(id) # Ou Question.query.get(id)
    if not question:
        return jsonify({"error": "Questão não encontrada"}), 404

    try:
        # 3. LIMPEZA DOS DADOS (Cascata Manual)
        # Primeiro apaga o histórico de respostas dessa questão
        UserAnswer.query.filter_by(question_id=id).delete()
        
        # Depois apaga as alternativas dessa questão
        Alternative.query.filter_by(question_id=id).delete()

        # Por fim, apaga a questão
        db.session.delete(question)
        
        db.session.commit()
        return jsonify({"message": "Questão excluída com sucesso!"}), 200

    except Exception as e:
        db.session.rollback()
        # Agora o erro vai aparecer detalhado no seu alert
        return jsonify({"error": str(e)}), 500