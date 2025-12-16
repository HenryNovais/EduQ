const API_URL = 'http://127.0.0.1:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserData();
    loadStats();
    setupTheme();
});

function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) window.location.href = '/';
}

function loadUserData() {
    const name = localStorage.getItem('userName') || 'Estudante';
    document.getElementById('user-name').textContent = name;
    document.getElementById('dropdown-name').textContent = name;
    document.getElementById('dropdown-email').textContent = 'henry@email.com'; // Pode vir do login
}

/* --- TEMA DARK/LIGHT --- */
function setupTheme() {
    const toggleBtn = document.getElementById('theme-toggle');
    const icon = toggleBtn.querySelector('i');
    // 1. Captura o elemento da logo pelo ID que criamos
    const logoImg = document.getElementById('theme-logo');

    toggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');

        // Verifica se o tema escuro está ativo
        if (document.body.classList.contains('dark-theme')) {
            // MODO ESCURO: Muda ícone para sol e logo para a branca
            icon.classList.replace('fa-moon', 'fa-sun');
            logoImg.src = '/static/img/logo2.png';
        } else {
            // MODO CLARO: Muda ícone para lua e logo para a roxa original
            icon.classList.replace('fa-sun', 'fa-moon');
            logoImg.src = '/static/img/logo.png';
        }
    });
}

/* --- MENU USUÁRIO --- */
const userBtn = document.getElementById('user-btn');
const dropdown = document.getElementById('user-dropdown');

userBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('show');
});

document.addEventListener('click', () => {
    dropdown.classList.remove('show');
});

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

/* --- ESTATÍSTICAS --- */
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats/dashboard`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();

        // Atualiza Números
        document.getElementById('stat-total').textContent = data.total_questions;
        document.getElementById('stat-accuracy').textContent = `${data.accuracy}%`;
        document.getElementById('stat-correct').textContent = data.correct_count;
        document.getElementById('stat-incorrect').textContent = data.incorrect_count;

        // Renderiza Barras de Progresso
        renderBars('strengths-container', data.subjects.filter(s => s.type === 'strength'), 'var(--success)');
        renderBars('weaknesses-container', data.subjects.filter(s => s.type === 'weakness'), 'var(--danger)');

    } catch (error) {
        console.error("Erro ao carregar stats", error);
    }
}

function renderBars(containerId, items, color) {
    const container = document.getElementById(containerId);
    container.innerHTML = items.map(item => `
        <div class="progress-item">
            <div class="progress-label">
                <span>${item.name}</span>
                <span>${item.score}%</span>
            </div>
            <div class="progress-bg">
                <div class="progress-fill" style="width: ${item.score}%; background-color: ${color};"></div>
            </div>
        </div>
    `).join('');
}

/* --- BUSCA E QUESTÕES --- */
async function loadQuestions() {
    const filters = {
        difficulty: document.getElementById('filter-difficulty').value
        // Adicionar outros filtros na query string
    };

    const response = await fetch(`${API_URL}/questions/search?difficulty=${filters.difficulty}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const questions = await response.json();

    renderQuestions(questions);

    // Mostra botão de nova busca
    document.getElementById('new-search-container').style.display = 'block';
    // Rola até as questões
    document.getElementById('questions-container').scrollIntoView({ behavior: 'smooth' });
}

function renderQuestions(questions) {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';

    questions.forEach(q => {
        const card = document.createElement('div');
        card.className = 'question-card';
        card.innerHTML = `
            <div class="tags">
                <span class="tag">ENEM</span>
                <span class="tag">Matemática</span>
                <span class="tag medium">${q.difficulty}</span>
            </div>
            <p style="margin-bottom: 20px; font-size: 1.1rem;">${q.statement}</p>
            <div class="alternatives-list" id="q-${q.id}">
                ${q.alternatives.map(alt => `
                    <div class="alternative" onclick="checkAnswer(${q.id}, ${alt.id}, this)">
                        ${alt.text}
                        <i class="fas status-icon"></i>
                    </div>
                `).join('')}
            </div>
            <div id="feedback-${q.id}" class="feedback-box" style="display:none"></div>
        `;
        container.appendChild(card);
    });
}

/* --- RESPONDER QUESTÃO --- */
async function checkAnswer(qId, altId, element) {
    // Impede clicar duas vezes
    if (element.parentElement.classList.contains('answered')) return;

    const response = await fetch(`${API_URL}/questions/check/${qId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ alternative_id: altId })
    });

    const result = await response.json();
    const container = document.getElementById(`q-${qId}`);
    const feedback = document.getElementById(`feedback-${qId}`);

    container.classList.add('answered');

    // Remove classes anteriores
    Array.from(container.children).forEach(child => child.classList.remove('selected'));

    if (result.correct) {
        element.classList.add('correct');
        element.querySelector('.status-icon').classList.add('fa-check-circle');
        feedback.className = 'feedback-box correct';
        feedback.innerHTML = `✅ <strong>Resposta Correta!</strong><br>${result.explanation}`;
    } else {
        element.classList.add('wrong');
        element.querySelector('.status-icon').classList.add('fa-times-circle');

        // Acha a correta para mostrar (Opcional)
        // const correctEl = ... lógica para pintar a correta de verde

        feedback.className = 'feedback-box wrong';
        feedback.innerHTML = `❌ <strong>Resposta Incorreta.</strong><br>${result.explanation}`;
    }
    feedback.style.display = 'block';
}

function resetSearch() {
    document.getElementById('questions-container').innerHTML = '';
    document.getElementById('new-search-container').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}