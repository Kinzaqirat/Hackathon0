const API_BASE = "/api";

async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();

        document.getElementById('active-tasks').innerText = data.active_tasks;
        document.getElementById('revenue').innerText = data.revenue;
        document.getElementById('completed-tasks').innerText = data.completed_tasks;
        document.getElementById('system-health').innerText = data.system_health;
    } catch (error) {
        console.error("Failed to fetch stats:", error);
    }
}

async function fetchTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks`);
        const tasks = await response.json();

        const taskList = document.getElementById('task-list');
        const emailList = document.getElementById('email-list');
        const emailCountBadge = document.getElementById('email-count');

        const emails = tasks.filter(t => t.type === 'email');
        const generalTasks = tasks.filter(t => t.type !== 'email');

        // Update Email Section
        if (emails.length === 0) {
            emailList.innerHTML = `<p style="color: var(--text-dim); text-align: center; padding: 2rem;">Inbox is clear.</p>`;
            emailCountBadge.innerText = "0 New";
        } else {
            emailCountBadge.innerText = `${emails.length} New`;
            emailList.innerHTML = emails.map(task => createTaskElement(task)).join('');
        }

        // Update General Tasks Section
        if (generalTasks.length === 0) {
            taskList.innerHTML = `<p style="color: var(--text-dim); text-align: center; padding: 2rem;">No pending missions.</p>`;
        } else {
            taskList.innerHTML = generalTasks.map(task => createTaskElement(task)).join('');
        }
    } catch (error) {
        console.error("Failed to fetch tasks:", error);
    }
}

function createTaskElement(task) {
    return `
        <div class="task-item" onclick="openTaskDetail('${task.id}')">
            <div class="task-icon">${task.type === 'email' ? '📧' : '📑'}</div>
            <div class="task-info">
                <h4>${task.title}</h4>
                ${task.sender ? `<small style="color: var(--primary); display: block; margin-bottom: 4px;">From: ${task.sender}</small>` : ''}
                <p>${task.snippet || 'Click to view details...'}</p>
                <small>${new Date(task.time * 1000).toLocaleString()}</small>
            </div>
        </div>
    `;
}

const taskModal = document.getElementById('task-modal');
const modalBody = document.getElementById('modal-body');
const modalTitle = document.getElementById('modal-title');
const closeTaskModal = document.getElementById('close-task-modal');
const replyBtn = document.getElementById('reply-btn');

const archiveBtn = document.getElementById('archive-btn');

async function openTaskDetail(taskId) {
    try {
        const response = await fetch(`${API_BASE}/task/${taskId}`);
        const data = await response.json();

        modalTitle.innerText = data.subject || taskId;
        modalBody.innerHTML = `
            <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border);">
                <span style="color: var(--primary); font-weight: bold;">From:</span> ${data.from}<br>
            </div>
            <div class="email-body-text" style="white-space: pre-wrap;">${data.body}</div>
        `;
        taskModal.classList.add('active');

        const sender = data.from;

        replyBtn.onclick = () => {
            taskModal.classList.remove('active');
            if (!chatContainer.classList.contains('active')) {
                chatContainer.classList.add('active');
            }
            chatInput.value = (sender && sender !== "Unknown") ? `write mail to ${sender}: ` : "write mail to ";
            chatInput.focus();
        };

        archiveBtn.onclick = async () => {
            archiveBtn.innerText = "Archiving...";
            try {
                const response = await fetch(`${API_BASE}/task/complete`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: taskId })
                });
                if (response.ok) {
                    taskModal.classList.remove('active');
                    await fetchTasks();
                    await fetchStats();
                } else {
                    const error = await response.json();
                    alert("Failed to archive task: " + (error.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("Archive error:", error);
            } finally {
                archiveBtn.innerText = "Mark as Done";
            }
        };
    } catch (error) {
        console.error("Failed to fetch task detail:", error);
    }
}

closeTaskModal.addEventListener('click', () => {
    taskModal.classList.remove('active');
});

window.onclick = (event) => {
    if (event.target == taskModal) {
        taskModal.classList.remove('active');
    }
}

async function fetchLogs() {
    try {
        const response = await fetch(`${API_BASE}/logs`);
        const logs = await response.json();

        const logFeed = document.getElementById('log-feed');
        if (logs.length === 0) {
            logFeed.innerHTML = `<p style="color: var(--text-dim);">No recent activity logged.</p>`;
            return;
        }

        logFeed.innerHTML = logs.map(log => `
            <div class="log-item">${log}</div>
        `).join('');
    } catch (error) {
        console.error("Failed to fetch logs:", error);
    }
}

function updateGreeting() {
    const hour = new Date().getHours();
    const greeting = document.getElementById('greeting');
    if (hour < 12) greeting.innerText = "Good Morning, CEO";
    else if (hour < 18) greeting.innerText = "Good Afternoon, CEO";
    else greeting.innerText = "Good Evening, CEO";
}

// Chat Functionality
const chatToggle = document.getElementById('chat-toggle');
const chatClose = document.getElementById('chat-close');
const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');
const chatMessages = document.getElementById('chat-messages');

chatToggle.addEventListener('click', () => {
    chatContainer.classList.toggle('active');
    document.getElementById('chat-badge').style.display = 'none';
});

chatClose.addEventListener('click', () => {
    chatContainer.classList.remove('active');
});

async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message to UI
    appendMessage('user', message);
    chatInput.value = '';

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (response.ok) {
            setTimeout(() => {
                appendMessage('bot', "Command received. I've placed the mission in your Inbox for processing.");
            }, 600);
        } else {
            appendMessage('bot', "Sorry, I had trouble communicating with the backend.");
        }
    } catch (error) {
        console.error("Chat error:", error);
        appendMessage('bot', "System error. Please ensure the API is running.");
    }
}

function appendMessage(type, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}-message`;
    msgDiv.innerText = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatSend.addEventListener('click', sendChatMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChatMessage();
});

// Initial fetch
fetchStats();
fetchTasks();
fetchLogs();
updateGreeting();

// Refresh every 5 seconds
setInterval(() => {
    fetchStats();
    fetchTasks();
    fetchLogs();
}, 5000);
