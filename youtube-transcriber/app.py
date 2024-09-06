from flask import Flask, render_template, request, jsonify
import requests
import openai
import time

app = Flask(__name__)

# AssemblyAI and OpenAI API Keys
ASSEMBLYAI_API_KEY = 'Insert API Key'
OPENAI_API_KEY = 'Insert API Key'


# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Function to send the MP3 URL to AssemblyAI for transcription
def transcribe_audio(audio_url):
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
    }
    response = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        json={'audio_url': audio_url},
        headers=headers
    )
    transcript_id = response.json().get('id')
    
    # Wait until transcription is complete
    transcript_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
    while True:
        result = requests.get(transcript_url, headers=headers).json()
        if result['status'] == 'completed':
            return result['text']
        elif result['status'] == 'failed':
            return "Transcription failed."
        time.sleep(3)  # Wait 3 seconds before checking again

# Function to ask a question about the podcast using OpenAI GPT
def ask_question(transcription, user_question):
    prompt = f"Podcast transcription: {transcription}\nQuestion: {user_question}\nAnswer:"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating answer: {str(e)}"


# Route for the home page (renders HTML template)
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the transcription of the podcast
@app.route('/transcribe', methods=['POST'])
def transcribe_podcast():
    mp3_url = request.form['mp3_url']
    transcription = transcribe_audio(mp3_url)
    return jsonify({"transcription": transcription})

# Route to handle user questions about the podcast
@app.route('/ask', methods=['POST'])
def ask_about_podcast():
    transcription = request.form['transcription']
    user_question = request.form['question']
    
    # Log for debugging
    print(f"Received transcription: {transcription[:50]}...")
    print(f"Received question: {user_question}")
    
    # Generate answer
    answer = ask_question(transcription, user_question)
    print(f"Generated answer: {answer}")  # Log the answer for debugging
    
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
