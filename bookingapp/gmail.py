from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http, ServerNotFoundError
from oauth2client import file, client, tools
from email.mime.text import MIMEText
import base64
from django.conf import settings

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.send'


def send(to, message_text="<p>mail from superbooking</p>", subject="Gmail API Test"):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)

    try:
        service = build('gmail', 'v1', http=creds.authorize(Http()))
    except ServerNotFoundError:
        print("An error has occurred: %s" % ServerNotFoundError)

    # Build message
    sender = "super School <{}>".format(settings.DEFAULT_FROM_EMAIL)
    message = create_message(sender, to , subject, message_text)

    # Call the Gmail API
    try:
        result = send_message(service, "me", message)
        print(result)
    except UnboundLocalError:
        print("An error has occurred: %s" % UnboundLocalError)
        print("Most likely, the API service failed to initialize.")
        print("The mail has not been sent.")


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text, 'html')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    encoded_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': encoded_message.decode()}


def send_message(service, user_id, message):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
    Sent Message.
    """
    try:
        message = (service.users().messages().send(
            userId=user_id,
            body=message).execute())

        print('Message Id: %s' % message['id'])
        return message
    except ServerNotFoundError:
        print('An error occurred: %s' % ServerNotFoundError)
        print('Most likely, the mailer could not connect to the server.')


if __name__ == '__main__':
    main()
