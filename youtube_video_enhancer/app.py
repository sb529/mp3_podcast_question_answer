from flask import Flask, request, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
import ssl

# Initialize Flask app
app = Flask(__name__)

# Your YouTube API key
API_KEY = 'AIzaSyASNcHwR0osBmMW6xQ9oqpN0eEB04e0DMw'

# Download necessary NLTK resources
def download_nltk_resources():
    try:
        # Disable SSL verification (use with caution)
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        resources = ['punkt_tab', 'stopwords']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                print(f"Downloading {resource}")
                nltk.download(resource, quiet=True)
    except Exception as e:
        print(f"Error downloading NLTK resources: {str(e)}")

# Call the function to download resources
download_nltk_resources()

# Function to get video transcript
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        return str(e)

# Function to extract keywords from transcript
def extract_keywords(transcript):
    try:
        words = word_tokenize(" ".join([t['text'] for t in transcript]))
        keywords = [word for word in words if word.isalnum() and word.lower() not in stopwords.words('english')]
        return keywords
    except Exception as e:
        print(f"Error in extract_keywords: {str(e)}")
        return []

# Function to fetch related videos using YouTube Data API
def get_related_videos(keywords):
    try:
        query = " ".join(keywords[:5])  # Use the top 5 keywords
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={API_KEY}&type=video"
        response = requests.get(search_url)
        related_videos = response.json()
        return related_videos.get('items', [])
    except Exception as e:
        print(f"Error in get_related_videos: {str(e)}")
        return []

# Home route to display the form
@app.route('/')
def home():
    return render_template('index.html')

# Function to get video details (title, etc.) using YouTube Data API
def get_video_details(video_id):
    try:
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=snippet"
        response = requests.get(url)
        video_info = response.json()
        title = video_info['items'][0]['snippet']['title']
        return title
    except Exception as e:
        print(f"Error fetching video details: {str(e)}")
        return None

# Route to handle form submission and show recommendations
@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    video_url = request.form['video_url']
    try:
        # Extract video ID from the URL
        video_id = video_url.split('v=')[-1].split('&')[0]
        
        # Get video title
        video_title = get_video_details(video_id)
        if not video_title:
            return "Error fetching video details."

        # Get transcript
        transcript = get_transcript(video_id)
        if isinstance(transcript, str):
            return f"Error fetching transcript: {transcript}"

        # Extract keywords from transcript
        keywords = extract_keywords(transcript)
        
        # Fetch related videos using the keywords
        related_videos = get_related_videos(keywords)
        
        # Render the same page with the recommendations and video title
        return render_template('index.html', videos=related_videos, video_title=video_title)

    except Exception as e:
        return f"An error occurred: {str(e)}"



# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)