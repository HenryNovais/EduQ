# 📘 EduQ - Plataforma de Questões e Estudos

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![Status](https://img.shields.io/badge/Status-Concluído-success)
![Deploy](https://img.shields.io/badge/Deploy-Render-purple)

**EduQ** é uma plataforma web completa para resolução de questões de vestibulares e concursos. O sistema oferece um ambiente interativo onde estudantes podem testar seus conhecimentos, receber feedback imediato e acompanhar seu desempenho através de um dashboard estatístico detalhado.

🔗 **Acesse o projeto online:** [[https://eduq-app.onrender.com](https://eduq.onrender.com)]

---

## 📸 Screenshots

| Dashboard do Aluno | Painel Administrativo |
|:------------------:|:---------------------:|
| ![Dashboard](https://via.placeholder.com/400x200?text=Dashboard+Image) | ![Admin](https://via.placeholder.com/400x200?text=Admin+Image) |

---

## 🚀 Funcionalidades Principais

### 👤 Para Estudantes
* **Resolução de Questões:** Interface limpa para responder questões de múltipla escolha.
* **Feedback Imediato:** O sistema informa na hora se a resposta está correta e fornece explicações.
* **Dashboard de Desempenho:**
    * Gráficos de taxa de acerto.
    * Identificação automática de **Pontos Fortes** e **Áreas de Melhoria** (baseado em % de acerto por matéria).
* **Filtros Inteligentes:** Busca por Instituição, Matéria, Tópico e Dificuldade.

### 🛡️ Para Administradores
* **CRUD Completo de Questões:** Criar, Editar e Excluir questões.
* **Gestão de Banco de Dados:** As alterações refletem imediatamente para os usuários.
* **Proteção de Rotas:** Acesso restrito via decorators e verificação de tokens.

### 🔐 Segurança e Arquitetura
* **Autenticação JWT:** Login seguro com tokens que expiram automaticamente.
* **Hash de Senhas:** Senhas criptografadas antes de salvar no banco (PBKDF2/SHA256).
* **Arquitetura MVC:** Separação clara entre Models, Views (Templates/Controllers) e Services.

---

## 🛠️ Tecnologias Utilizadas

### Backend
* **Python 3**
* **Flask** (Framework Web)
* **SQLAlchemy** (ORM para Banco de Dados)
* **Flask-JWT-Extended** (Autenticação)

### Frontend
* **HTML5 & CSS3** (Design Responsivo)
* **JavaScript (Vanilla)** (Consumo de API Fetch e Manipulação do DOM)

### Banco de Dados & Infraestrutura
* **Desenvolvimento:** MySQL (Local)
* **Produção:** PostgreSQL (Render)
* **Hospedagem:** Render.com

---

## ⚙️ Como rodar o projeto localmente

Siga os passos abaixo para testar o EduQ na sua máquina:

### 1. Clone o repositório
```bash
git clone [https://github.com/HenryNovais/EduQ.git](https://github.com/HenryNovais/EduQ.git)
cd EduQ
```

---

## 2. Crie e ative um ambiente virtual
# Windows
```Bash
python -m venv venv
venv\Scripts\activate
```

# Linux/Mac
```Bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Instale as dependências
```Bash
pip install -r requirements.txt
```
---

## 4. Configuração do Banco de Dados
O sistema está configurado para usar MySQL localmente.
  1. Crie um banco de dados no seu MySQL chamado vestibular_db.
  2. No arquivo config.py, ajuste a URI se necessário (usuário/senha):
```Python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:SUA_SENHA@localhost/vestibular_db'
```

---

## 5. Execute o projeto
```Bash
python run.py
```
O servidor iniciará em http://127.0.0.1:5000.
  Nota: Na primeira execução, o sistema criará automaticamente as tabelas e um usuário Admin padrão (se configurado no run.py).

---

📂 Estrutura do Projeto
EduQ/

├── app/

│   ├── controllers/    # Rotas da API (Auth, Questions, Stats)

│   ├── models/         # Classes do Banco de Dados

│   ├── repositories/   # Consultas SQL

│   ├── services/       # Regras de Negócio

│   └── __init__.py     # Inicialização do App Factory

├── static/             # CSS, JS e Imagens

├── templates/          # Arquivos HTML

├── tests/              # Testes Automatizados

├── config.py           # Configurações de Ambiente

├── run.py              # Ponto de Entrada

└── requirements.txt    # Dependências

---

🤝 Contribuição
Desenvolvido por Henry Novais Calmon. Projeto realizado como parte dos estudos em Desenvolvimento Full Stack e Engenharia de Software.

📧 Contato: henryncalmon05@gmail.com
