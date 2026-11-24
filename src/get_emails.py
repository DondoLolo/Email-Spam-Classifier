from email.quoprimime import body_length

from google.auth.transport.requests import Request # Refreshes log in if permission expires
from google.oauth2.credentials import Credentials #Turns token.json into something python can use
from google_auth_oauthlib.flow import InstalledAppFlow # Handles Browser login process
from googleapiclient.discovery import build # Creates actual gmail connection
import os # Used to access files on computer
import base64 # Decodes encoded bodies of emails
import pandas as pd
from bs4 import BeautifulSoup # Html text parser
import os #filepath helper

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'] # Tells google what app wants permission to do


def create_service():
    creds = None # Creates a variable that will eventually store my google login info

    if os.path.exists('credentials/token.json'): # Have I logged into Google before?
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        ) # Loads saved login ^^^

    if not creds or not creds.valid: # Do I have a working login?

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request()) # Gets new permission token without making you sign in again
        else:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            credentials_path = os.path.join(BASE_DIR, 'Credentials', 'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                SCOPES
            ) # Tells Google: This is the app requesting access

            creds = flow.run_local_server(port=0) # Opens sign in window

        with open("token.json","w") as token:
         token.write(creds.to_json()) # Creates token.json

    service = build( # Creates the object that lets Python talk to Gmail
        "gmail",
        "v1",
        credentials = creds
    )

    return service

service = create_service() # Object that lets Python talk to Gmail

print("Gmail Connected!")
print()

emails = pd.DataFrame(columns = ['Subject', 'Sender', 'Body', 'Spam']) # Dataframe for email data

def get_emails(service): # Returns or prints emails

    results = service.users().messages().list(
        userId = "me",
        maxResults = 9
    ).execute()

    messages = results.get("messages", [])

    for message in messages: # Loops through each email
        msg = service.users().messages().get(
            userId="me",
            id = message["id"]
        ).execute()

        headers = msg['payload']['headers']
        parts = msg['payload'].get('parts', [])

        body = get_email_body(parts)
       # print(body)

        #prints subject and from for each email
        for header in headers:
            if header['name'] == 'Subject':
                #print("Subject: ", header['value'])
                subject = header['value']

            if header['name'] == "From":
               # print("From: ", header['value'])
                sender = header['value']

        new_rows = [subject, sender, body, 0 ]
        emails.loc[len(emails)] = new_rows # Adds set to dataframe of emails

# Gets the body text of an email bc its decoded
def get_email_body(parts):
    html_body = None
    text_body = None

    for part in parts:

        mime_type = part.get("mimeType")

        # Look for HTML
        if mime_type == "text/html":
            data = part["body"]["data"]
            html = base64.urlsafe_b64decode(data).decode("utf-8")

            soup = BeautifulSoup(html, "html.parser")
            html_body = soup.get_text(separator=" ", strip=True)

        # Look for plain text
        elif mime_type == "text/plain":
            data = part["body"]["data"]
            text_body = base64.urlsafe_b64decode(data).decode("utf-8")

        # Search inside nested parts
        elif "parts" in part:
            body = get_email_body(part["parts"])

            if body:
                return body

    # Prefer HTML if available
    if html_body:
        return html_body

    if text_body:
        return text_body

    return ""
get_emails(service)
print(emails)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, 'data', 'emails.csv')
training_path = os.path.join(BASE_DIR,'ai_model','training_emails.csv')

emails.to_csv(data_path, index = False)
emails.to_csv(training_path, index = False)