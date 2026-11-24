from src.get_emails import create_service, get_email_body, get_emails

service = create_service()

# Create Label
service.users().labels().create(
    userId='me',
    body={
        'name' : "College Spam"
    }
).execute()

labels = service.users().labels().list(userId = "me").execute()

for label in labels['labels']:
    if label['name'] == 'College Spam':
        label_id = label['id']
print(label_id)

#Predict

