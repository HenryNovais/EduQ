from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Importante para o frontend acessar
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app) # Habilita CORS

    from app.controllers.auth_controller import auth_bp
    from app.controllers.question_controller import question_bp
    from app.controllers.stats_controller import stats_bp

    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(question_bp, url_prefix='/api/questions')
    
    # Rota para servir o Frontend
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        from flask import render_template
        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard():
        from flask import render_template
        return render_template('dashboard.html')

    return app