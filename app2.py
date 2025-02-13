import os
import base64
import streamlit as st
import google.generativeai as genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re

# Set up Google Generative AI API (Gemini)
genai.configure(api_key="AIzaSyDY4OLN8P4jkMo_zcrrNDjIe-GsbpHZ03I")  # Replace with your actual API key

# Set up Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRET_FILE = 'credentials.json'  # Path to the credentials.json file from Google Cloud

# Authenticate and build the Gmail API service
def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

# Fetch unread emails
def get_unread_emails(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = results.get('messages', [])
    
    email_list = []
    
    if not messages:
        return []

    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        email_data = {
            'id': msg['id'],
            'snippet': message['snippet'],
            'from': '',
            'subject': '',
            'date': ''
        }
        for header in message['payload']['headers']:
            if header['name'] == 'From':
                email_data['from'] = header['value']
            elif header['name'] == 'Subject':
                email_data['subject'] = header['value']
            elif header['name'] == 'Date':
                email_data['date'] = header['value']
        
        email_list.append(email_data)
    
    return email_list

# Summarize email content with AI
def summarize_email(text):
    try:
        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(f"Summarize the following email: {text}")
        return response.text.strip()
    except Exception as e:
        return f"Error summarizing: {e}"

# Compose email reply using AI
def compose_reply(original_email, user_input):
    try:
        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(f"Compose a polite response to the following email:\n\n{original_email}\n\nUser input: {user_input}")
        return response.text.strip()
    except Exception as e:
        return f"Error composing reply: {e}"

# Send email
def send_email(service, to, subject, body):
    message = {
        'raw': base64.urlsafe_b64encode(f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}".encode('utf-8')).decode('utf-8')
    }
    try:
        service.users().messages().send(userId='me', body=message).execute()
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

# Streamlit interface
def main():
    st.title("AI-Powered Email Assistant")

    # Authenticate Gmail
    service = authenticate_gmail()

    # Fetch unread emails
    unread_emails = get_unread_emails(service)

    if unread_emails:
        st.subheader("Unread Emails")
        for email in unread_emails:
            st.markdown(f"**From**: {email['from']}")
            st.markdown(f"**Subject**: {email['subject']}")
            st.markdown(f"**Snippet**: {email['snippet']}")
            
            # Option to summarize email
            if st.button(f"Summarize: {email['subject']}"):
                summary = summarize_email(email['snippet'])
                st.markdown(f"**Summary**: {summary}")

            # Option to compose a reply
            user_reply = st.text_area(f"Your reply to: {email['subject']}", "")
            if st.button(f"Compose Reply to: {email['subject']}"):
                reply = compose_reply(email['snippet'], user_reply)
                st.markdown(f"**Reply**: {reply}")
            
            # Send button for custom email composition
            send_to = st.text_input("To:", email['from'])
            send_subject = st.text_input("Subject:", "RE: " + email['subject'])
            send_body = st.text_area("Body:", "Dear " + email['from'] + ",\n\n")
            if st.button("Send Email"):
                send_status = send_email(service, send_to, send_subject, send_body)
                st.success(send_status)

    else:
        st.write("No unread emails found.")

if __name__ == '__main__':
    main()
