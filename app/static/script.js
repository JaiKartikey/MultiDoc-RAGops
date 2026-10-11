// Upload form handler
const uploadForm = document.getElementById('upload-form');
if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const fileInput = document.getElementById('file-input');
        const uploadBtn = document.getElementById('upload-btn');
        const uploadStatus = document.getElementById('upload-status');

        if (!fileInput.files || fileInput.files.length === 0) return;

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        uploadBtn.disabled = true;
        fileInput.disabled = true;
        uploadStatus.className = 'status-badge status-loading';
        uploadStatus.textContent = `Uploading and ingesting "${file.name}"...`;
        uploadStatus.style.display = 'block';

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Upload failed');
            }

            uploadStatus.className = 'status-badge status-success';
            uploadStatus.textContent = `✓ ${data.message} Total knowledge base chunks: ${data.total_chunks}.`;
            uploadForm.reset();
        } catch (err) {
            uploadStatus.className = 'status-badge status-error';
            uploadStatus.textContent = `✗ Error: ${err.message}`;
        } finally {
            uploadBtn.disabled = false;
            fileInput.disabled = false;
        }
    });
}

// Ask question form handler
document.getElementById('ask-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const questionInput = document.getElementById('question');
    const submitBtn = document.getElementById('submit-btn');
    const loading = document.getElementById('loading');
    const resultContainer = document.getElementById('result-container');
    const errorMsg = document.getElementById('error-message');

    const question = questionInput.value.trim();
    if (!question) return;

    // Reset UI state
    submitBtn.disabled = true;
    questionInput.disabled = true;
    loading.style.display = 'block';
    resultContainer.style.display = 'none';
    errorMsg.style.display = 'none';
    document.getElementById('sources-list').innerHTML = '';

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred while processing the request.');
        }

        // Populate UI
        document.getElementById('answer-text').textContent = data.answer;

        // Populate metrics
        document.getElementById('latency').textContent = data.latency.toFixed(3);
        document.getElementById('retrieval-latency').textContent = data.retrieval_latency.toFixed(3);
        document.getElementById('generation-latency').textContent = data.generation_latency.toFixed(3);

        // Populate sources
        const sourcesList = document.getElementById('sources-list');
        data.sources.forEach((source, index) => {
            const sourceDiv = document.createElement('div');
            sourceDiv.className = 'source-card';
            sourceDiv.innerHTML = `
                <div class="source-header">
                    <span>Source ${index + 1}</span>
                    <span>Relevance Score: ${source.score.toFixed(3)}</span>
                </div>
                <div>${source.chunk}</div>
            `;
            sourcesList.appendChild(sourceDiv);
        });

        resultContainer.style.display = 'block';

    } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        questionInput.disabled = false;
        loading.style.display = 'none';
        questionInput.focus();
    }
});
