from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

# Alteração aqui: adicione o parâmetro test_config=None
def create_app(test_config=None):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    if test_config is None:
        # Se não passar config de teste, usa a config normal (MySQL)
        app.config.from_object(Config)
    else:
        # Se passar config de teste, usa ela (SQLite em memória)
        app.config.from_mapping(test_config)
    
    db.init_app(app)
    CORS(app)

    from app.controllers.auth_controller import auth_bp
    from app.controllers.question_controller import question_bp
    from app.controllers.stats_controller import stats_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(question_bp, url_prefix='/api/questions')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        from flask import render_template
        return render_template('dashboard.html')

    @app.route('/register')
    def register_page():
        from flask import render_template
        return render_template('register.html')

    return app