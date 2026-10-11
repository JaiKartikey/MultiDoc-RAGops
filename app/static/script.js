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
