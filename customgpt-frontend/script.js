document.getElementById('send-btn').addEventListener('click', function() {
    let userInput = document.getElementById('user-input').value;
    let chatOutput = document.getElementById('chat-output');
    
    // Display user's question
    chatOutput.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;
    
    // Send the question to your custom GPT (this is where you'd integrate your GPT API)
    fetch('https://your-gpt-api-endpoint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Display GPT's response
        chatOutput.innerHTML += `<p><strong>GPT:</strong> ${data.response}</p>`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('excel-file');
    const analyzeBtn = document.getElementById('analyze-btn');
    const recommendationsSection = document.getElementById('recommendations');
    const recommendationsContent = document.getElementById('recommendations-content');

    analyzeBtn.addEventListener('click', async () => {
        if (!fileInput.files.length) {
            alert('Please select an Excel file first.');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';

            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('API request failed');
            }

            const data = await response.json();

            // Display recommendations
            recommendationsContent.innerHTML = `<p>${data.insights}</p>`;
            recommendationsSection.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while analyzing the file. Please try again.');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze Data';
        }
    });
});
