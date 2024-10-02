from flask import Flask, render_template, request
from scraper import scrape_website
from chatbot import ask_question

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', question=None, answer=None)

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    website_content = scrape_website()
    answer = ask_question(question, website_content)
    return render_template('index.html', question=None, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
