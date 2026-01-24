const API_URL = 'http://127.0.0.1:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserData();
    loadStats();
    setupTheme();
    loadFilterOptions();
    const isAdmin = localStorage.getItem('isAdmin') === 'true'; // O localStorage salva como string
    if (isAdmin) {
        document.getElementById('admin-btn').style.display = 'inline-block';
    }
});

function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) window.location.href = '/';
}

function loadUserData() {
    const name = localStorage.getItem('userName') || 'Estudante';
    const email = localStorage.getItem('userEmail') || 'usuario@eduq.com'; // Pega do localStorage

    document.getElementById('user-name').textContent = name;

    // Atualiza os dados dentro do menu suspenso (Dropdown)
    document.getElementById('dropdown-name').textContent = name;
    document.getElementById('dropdown-email').textContent = email; // Agora mostra o email certo!
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
    const difficulty = document.getElementById('filter-difficulty').value;
    const institution = document.getElementById('filter-institution').value;
    const subject = document.getElementById('filter-subject').value;
    const topic = document.getElementById('filter-topic').value;

    // Monta a URL com todos os parâmetros
    const params = new URLSearchParams({
        difficulty,
        institution,
        subject,
        topic
    });

    const response = await fetch(`${API_URL}/questions/search?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const questions = await response.json();

    renderQuestions(questions);

    document.getElementById('new-search-container').style.display = 'block';
}

function renderQuestions(questions) {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';

    if (questions.length === 0) {
        container.innerHTML = '<p style="text-align:center; color: #666;">Nenhuma questão encontrada com esses filtros.</p>';
        return;
    }

    

    questions.forEach(q => {
        const card = document.createElement('div');
        card.className = 'question-card';

        const isAdmin = localStorage.getItem('isAdmin') === 'true';

        // Tradutor simples de dificuldade para PT-BR
        const diffMap = { 'EASY': 'Fácil', 'MEDIUM': 'Médio', 'HARD': 'Difícil' };
        const diffLabel = diffMap[q.difficulty] || q.difficulty;

        let deleteBtn = '';
        if (isAdmin) {
            deleteBtn = `
                <button onclick="deleteQuestion(${q.id})" style="float:right; color:red; background:none; border:none; cursor:pointer;" title="Excluir Questão">
                    <i class="fas fa-trash"></i>
                </button>
            `;
        }

        // AQUI ESTÁ A CORREÇÃO VISUAL: Usamos q.institution, q.subject, etc.
        card.innerHTML = `
            ${deleteBtn}<div class="tags">
                <span class="tag" style="background:#e3f2fd; color:#0d47a1;">${q.institution}</span>
                <span class="tag" style="background:#f3e5f5; color:#4a148c;">${q.subject}</span>
                <span class="tag" style="background:#e8f5e9; color:#1b5e20;">${q.topic}</span>
                <span class="tag medium">${diffLabel}</span>
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

// Função para chamar a API de Delete
async function deleteQuestion(id) {
    if (!confirm("Tem certeza que deseja excluir esta questão?")) return;

    try {
        const res = await fetch(`${API_URL}/questions/delete/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (res.ok) {
            alert("Questão excluída!");
            loadQuestions(); // Recarrega a lista
        } else {
            const data = await res.json();
            alert("Erro: " + (data.error || "Desconhecido"));
        }
    } catch (e) {
        console.error(e);
    }
}

async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_URL}/questions/options`);
        const data = await response.json();

        // Função auxiliar para preencher select
        const fillSelect = (id, items) => {
            const select = document.getElementById(id);
            // Mantém apenas a primeira opção (Todas)
            select.innerHTML = select.options[0].outerHTML;
            items.forEach(item => {
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item;
                select.appendChild(option);
            });
        };

        fillSelect('filter-institution', data.institutions);
        fillSelect('filter-subject', data.subjects);
        fillSelect('filter-topic', data.topics);

    } catch (error) {
        console.error("Erro ao carregar filtros:", error);
    }
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


/* --- EDITAR PERFIL --- */

function openProfileModal() {
    const modal = document.getElementById('profile-modal');

    // Preenche dados
    document.getElementById('edit-name').value = localStorage.getItem('userName') || '';
    document.getElementById('edit-email').value = localStorage.getItem('userEmail') || '';

    // Limpa campos de senha
    document.getElementById('current-password').value = '';
    document.getElementById('new-password').value = '';

    document.getElementById('user-dropdown').classList.remove('show');
    modal.style.display = 'flex';
}

function closeProfileModal() {
    document.getElementById('profile-modal').style.display = 'none';
}

async function saveProfile() {
    const name = document.getElementById('edit-name').value;
    const currentPass = document.getElementById('current-password').value;
    const newPass = document.getElementById('new-password').value;

    // Monta o objeto de envio
    const body = { name: name };

    // Só envia senha se o usuário digitou algo na "Nova Senha"
    if (newPass) {
        if (!currentPass) {
            alert("⚠️ Atenção: Para definir uma nova senha, você precisa digitar sua senha atual.");
            document.getElementById('current-password').focus();
            return;
        }
        body.current_password = currentPass;
        body.new_password = newPass;
    }

    try {
        const response = await fetch(`${API_URL}/auth/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (response.ok) {
            alert('✅ Perfil atualizado com sucesso!');
            localStorage.setItem('userName', data.name);
            document.getElementById('user-name').textContent = data.name;
            closeProfileModal();
        } else {
            alert('❌ Erro: ' + data.error);
        }
    } catch (error) {
        console.error(error);
        alert('Erro de conexão ao atualizar perfil.');
    }
}