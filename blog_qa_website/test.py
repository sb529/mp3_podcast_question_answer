import requests
from bs4 import BeautifulSoup

# Replace this URL with the URL of the Substack blog post you want to scrape
blog_url = 'https://apoorv03.com/'

def fetch_blog_content(blog_url):
    try:
        # Send a GET request to the blog URL
        response = requests.get(blog_url)
        
        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            return f"Error: Unable to access the blog post (status code {response.status_code})"
        
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find the main blog content
        article_content = soup.find('article')  # Adjust the tag and class based on the blog structure

        if article_content:
            content_text = article_content.get_text(separator=' ', strip=True)
            return content_text
        else:
            return "Error: Unable to find the blog content on this page."
    
    except Exception as e:
        return str(e)

# Call the function and print the result
blog_content = fetch_blog_content(blog_url)
print(blog_content)
