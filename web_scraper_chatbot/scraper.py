import requests
from bs4 import BeautifulSoup

def scrape_website():
    url = "https://apoorv03.com/"  # Hardcoded URL for the blog
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ')
            return text
        else:
            return f"Failed to retrieve content. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"
