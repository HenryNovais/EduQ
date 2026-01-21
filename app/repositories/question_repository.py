from app.models.models import Question, Institution, Topic, Subject
from app import db

class QuestionRepository:
    @staticmethod
    def get_all_filtered(filters):
        query = Question.query
        
        # Join necessário para filtrar por nomes (Matéria e Assunto estão em outras tabelas)
        query = query.join(Question.topic).join(Topic.subject)
        
        # Filtro de Dificuldade
        if filters.get('difficulty') and filters['difficulty'] != 'Todas':
            query = query.filter(Question.difficulty == filters['difficulty'])
            
        # Filtro de Instituição
        if filters.get('institution') and filters['institution'] != 'Todas':
            query = query.join(Question.institution).filter(Institution.name == filters['institution'])
            
        # Filtro de Matéria (Subject)
        if filters.get('subject') and filters['subject'] != 'Todas':
            query = query.filter(Subject.name == filters['subject'])
            
        # Filtro de Assunto (Topic)
        if filters.get('topic') and filters['topic'] != 'Todos':
            query = query.filter(Topic.name == filters['topic'])
        
        return query.all()

    @staticmethod
    def get_by_id(question_id):
        return Question.query.get(question_id)

    # Novo método para preencher os Dropdowns
    @staticmethod
    def get_filter_options():
        return {
            "institutions": [i.name for i in Institution.query.all()],
            "subjects": [s.name for s in Subject.query.all()],
            "topics": [t.name for t in Topic.query.all()]
        }