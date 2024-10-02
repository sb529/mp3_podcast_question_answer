from flask import Flask, render_template, request, jsonify
import openai
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Set your OpenAI API Key
openai.api_key = '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'

# Function to scrape Substack blog content using BeautifulSoup
def fetch_blog_content(blog_url):
    try:
        # Send a request to the blog URL
        response = requests.get(blog_url)
        
        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            return f"Error: Unable to access the blog post (status code {response.status_code})"
        
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Modify this line depending on your blog’s structure.
        # Most Substack blogs use <article> or <div> tags for the main content.
        article_content = soup.find('article')

        if article_content:
            content_text = article_content.get_text(separator=' ', strip=True)
            return content_text
        else:
            return "Error: Unable to find the blog content on this page."
    
    except Exception as e:
        return str(e)

# OpenAI API call for answering questions using GPT-3.5 Turbo
def get_answer_from_openai(content, user_question):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions based on blog content."},
        {"role": "user", "content": f"Based on the following blog content: {content}, answer this question: {user_question}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask_question', methods=['POST'])
def ask_question():
    blog_url = request.form['blog_url']
    user_question = request.form['question']

    # Fetch blog content
    blog_content = fetch_blog_content(blog_url)

    # If there's an error fetching the blog content, return the error
    if "Error" in blog_content:
        return jsonify({'answer': blog_content})

    # Get response from OpenAI
    answer = get_answer_from_openai(blog_content, user_question)

    return jsonify({'answer': answer})

if __name__ == "__main__":
    app.run(debug=True)
