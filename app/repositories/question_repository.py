from app.models.models import Question, Alternative

class QuestionRepository:
    @staticmethod
    def get_all_filtered(filters):
        query = Question.query
        
        if 'difficulty' in filters and filters['difficulty'] != 'Todas':
            query = query.filter_by(difficulty=filters['difficulty'])
            
        # Adicionar outros filtros (materia, assunto) aqui conforme necessidade
        
        return query.all()

    @staticmethod
    def get_by_id(question_id):
        return Question.query.get(question_id)