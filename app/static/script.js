// ─── State ────────────────────────────────────────────────────────────────────
const state = {
    messages: [],          // { role: 'user'|'ai', content, sources, latency }
    documents: [],         // { filename, chunks_added, total_chunks }
    isLoading: false,
};

// ─── DOM refs ─────────────────────────────────────────────────────────────────
const messagesEl     = document.getElementById('messages');
const emptyState     = document.getElementById('empty-state');
const questionInput  = document.getElementById('question-input');
const sendBtn        = document.getElementById('send-btn');
const fileInput      = document.getElementById('file-input');
const uploadZone     = document.getElementById('upload-zone');
const uploadStatus   = document.getElementById('upload-status');
const docList        = document.getElementById('doc-list');
const newChatBtn     = document.getElementById('new-chat-btn');

// ─── Textarea auto-resize ─────────────────────────────────────────────────────
questionInput.addEventListener('input', () => {
    questionInput.style.height = 'auto';
    questionInput.style.height = Math.min(questionInput.scrollHeight, 160) + 'px';
    sendBtn.disabled = questionInput.value.trim() === '' || state.isLoading;
});

// Send on Enter (Shift+Enter = new line)
questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) handleSend();
    }
});

sendBtn.addEventListener('click', handleSend);

// ─── Suggestion chips ─────────────────────────────────────────────────────────
document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
        questionInput.value = chip.dataset.q;
        questionInput.dispatchEvent(new Event('input'));
        questionInput.focus();
    });
});

// ─── New Chat ─────────────────────────────────────────────────────────────────
newChatBtn.addEventListener('click', () => {
    state.messages = [];
    messagesEl.innerHTML = '';
    emptyState.classList.remove('hidden');
    questionInput.value = '';
    questionInput.style.height = 'auto';
    sendBtn.disabled = true;
});

// ─── Send question ────────────────────────────────────────────────────────────
async function handleSend() {
    const question = questionInput.value.trim();
    if (!question || state.isLoading) return;

    state.isLoading = true;
    sendBtn.disabled = true;
    questionInput.value = '';
    questionInput.style.height = 'auto';

    emptyState.classList.add('hidden');

    // Append user message
    appendMessage('user', question);

    // Typing indicator
    const typingRow = appendTyping();

    try {
        const res = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });

        const data = await res.json();
        typingRow.remove();

        if (!res.ok) {
            const msg = Array.isArray(data.detail)
                ? data.detail.map(d => d.msg).join(', ')
                : (data.detail || 'An unexpected error occurred.');
            appendMessage('error', `⚠️ ${msg}`);
        } else {
            appendMessage('ai', data.answer, data.sources, {
                latency: data.latency,
                retrieval: data.retrieval_latency,
                generation: data.generation_latency,
            });
        }
    } catch (err) {
        typingRow.remove();
        appendMessage('error', `⚠️ Network error: ${err.message}`);
    } finally {
        state.isLoading = false;
        sendBtn.disabled = questionInput.value.trim() === '';
        scrollToBottom();
    }
}

// ─── Render helpers ───────────────────────────────────────────────────────────
function appendMessage(role, content, sources = [], latency = null) {
    const isUser  = role === 'user';
    const isError = role === 'error';
    const isAI    = role === 'ai';

    const row = document.createElement('div');
    row.className = `msg-row ${isUser ? 'user' : 'ai'}`;

    const avatarText = isUser ? 'You' : '🤖';
    const avatarClass = isUser ? 'user-avatar' : 'ai-avatar';
    const senderName = isUser ? 'You' : 'RAGOps AI';

    let sourcesHTML = '';
    if (isAI && sources && sources.length > 0) {
        const topScore = (sources[0].score * 100).toFixed(0);
        const chips = sources.map((s, i) => `
            <div class="source-chip">
                <strong>Source ${i + 1}</strong>
                <span>${escapeHtml(s.chunk)}</span>
                <span class="source-score">${(s.score * 100).toFixed(1)}%</span>
            </div>
        `).join('');
        sourcesHTML = `
            <details class="sources-accordion">
                <summary class="sources-summary">
                    <svg class="chevron" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                    <span>Retrieved Sources (${sources.length})</span>
                    <span class="sources-top-score">Top: ${topScore}% match</span>
                </summary>
                <div class="sources-list">
                    ${chips}
                </div>
            </details>`;
    }

    let latencyHTML = '';
    if (isAI && latency) {
        latencyHTML = `
            <div class="latency-bar">
                <span>Total: <b>${latency.latency.toFixed(2)}s</b></span>
                <span>Retrieval: <b>${latency.retrieval.toFixed(2)}s</b></span>
                <span>Generation: <b>${latency.generation.toFixed(2)}s</b></span>
            </div>`;
    }

    row.innerHTML = `
        <div class="msg-inner">
            <div class="avatar ${avatarClass}">${isUser ? 'You' : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>'}</div>
            <div class="bubble">
                <p class="bubble-name">${senderName}</p>
                <div class="bubble-content ${isError ? 'error-bubble' : ''}">${isUser ? escapeHtml(content) : (isError ? escapeHtml(content) : formatMarkdown(content))}</div>
                ${sourcesHTML}
                ${latencyHTML}
            </div>
        </div>`;

    messagesEl.appendChild(row);
    scrollToBottom();
    return row;
}

function appendTyping() {
    const row = document.createElement('div');
    row.className = 'msg-row ai';
    row.innerHTML = `
        <div class="msg-inner">
            <div class="avatar ai-avatar">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
                </svg>
            </div>
            <div class="bubble">
                <p class="bubble-name">RAGOps AI</p>
                <div class="bubble-content">
                    <div class="typing-indicator">
                        <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                    </div>
                </div>
            </div>
        </div>`;
    messagesEl.appendChild(row);
    scrollToBottom();
    return row;
}

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function formatMarkdown(text) {
    if (!text) return '';
    let html = escapeHtml(text);
    // Bold: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code style="background:var(--card);padding:2px 5px;border-radius:4px;font-size:0.88em;color:#e2e8f0;">$1</code>');
    // Bullet lists starting with * or -
    html = html.replace(/^\s*[\*\-]\s+(.*)$/gim, '• $1');
    return html;
}

// ─── File Upload ──────────────────────────────────────────────────────────────
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
});
uploadZone.addEventListener('click', (e) => {
    if (e.target.classList.contains('upload-link') || e.target === uploadZone || e.target.closest('.upload-zone')) {
        fileInput.click();
    }
});
fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleUpload(fileInput.files[0]);
    fileInput.value = '';
});

async function handleUpload(file) {
    const allowed = ['.txt', '.md', '.pdf', '.docx', '.csv'];
    const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowed.includes(ext)) {
        showUploadStatus('error', `✗ Unsupported file type. Allowed: PDF, DOCX, TXT, MD, CSV.`);
        return;
    }

    showUploadStatus('loading', `Uploading "${file.name}"…`);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) {
            showUploadStatus('error', `✗ ${data.detail || 'Upload failed.'}`);
        } else {
            showUploadStatus('success', `✓ "${data.filename}" ingested — ${data.chunks_added} new chunks added.`);
            addDocToSidebar(data);
        }
    } catch (err) {
        showUploadStatus('error', `✗ Network error: ${err.message}`);
    }
}

function showUploadStatus(type, msg) {
    uploadStatus.textContent = msg;
    uploadStatus.className = `upload-status ${type}`;
    uploadStatus.style.display = 'block';
    if (type === 'success') {
        setTimeout(() => { uploadStatus.style.display = 'none'; }, 5000);
    }
}

function addDocToSidebar(data) {
    const existing = document.querySelector('.no-docs');
    if (existing) existing.remove();

    const item = document.createElement('div');
    item.className = 'doc-item';
    item.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
        </svg>
        <span class="doc-item-name" title="${escapeHtml(data.filename)}">${escapeHtml(data.filename)}</span>
        <span class="doc-item-chunks">${data.chunks_added} chunks</span>
    `;
    docList.appendChild(item);
    state.documents.push(data);
}
