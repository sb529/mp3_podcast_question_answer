import os
import base64
import openai
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Gmail API authentication
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_latest_email(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='from:summarygen8@gmail.com').execute()
    messages = results.get('messages', [])
    if not messages:
        print("No new messages.")
        return None
    message = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    return message

def extract_email_content(message):
    if 'data' in message['payload']['body']:
        data = message['payload']['body']['data']
        decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
        return decoded_data
    return ""

def summarize_text(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize the following email thread:\n\n{text}",
        max_tokens=300
    )
    return response.choices[0].text.strip()

def send_summary(service, message, summary):
    email_text = f"To: {message['payload']['headers'][0]['value']}\n"
    email_text += f"Subject: Your Email Summary\n\n"
    email_text += f"Here is your email summary:\n\n{summary}"
    
    message = {
        'raw': base64.urlsafe_b64encode(email_text.encode()).decode()
    }
    service.users().messages().send(userId='me', body=message).execute()

if __name__ == '__main__':
    service = authenticate_gmail()
    email = get_latest_email(service)
    if email:
        email_content = extract_email_content(email)
        summary = summarize_text(email_content)
        send_summary(service, email, summary)
