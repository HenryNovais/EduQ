from app import create_app, db
from app.models.models import User
from werkzeug.security import generate_password_hash

app = create_app()

# --- BLOCO MÁGICO DE INICIALIZAÇÃO (PARA O RENDER) ---
with app.app_context():
    # 1. Cria as tabelas do banco (se não existirem)
    db.create_all()
    
    # 2. Verifica se o Admin já existe. Se não, cria ele.
    if not User.query.filter_by(email="henryncalmon05@gmail.com").first():
        print("Criando usuário Admin inicial...")
        admin = User(
            name="Henry Novais", 
            email="henryncalmon05@gmail.com", 
            password_hash=generate_password_hash("123456"), # <--- Coloque sua senha aqui
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin criado com sucesso!")
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
    # ADICIONE ESTAS DUAS LINHAS:
    print("--- CONECTANDO EM: ---")
    print(app.config.get('SQLALCHEMY_DATABASE_URI'))
    print("----------------------")
    
    app.run(debug=True)
