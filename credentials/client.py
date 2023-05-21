from __future__ import print_function
import logging
from google_access_share_bot.bot_logging import BotLoggingHandler

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

link = '1KA0j5SLv4zE_fF20tqzplyls8Zrcf3q8WqoZXoqE89I'
mail = 'msavkov10@gmail.com'
class Client:

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.logger = logging.getLogger('client')
        self.setup_logger()
        self.client = self.get_client()

    def setup_logger(self):
        handler = BotLoggingHandler(self.bot, self.chat_id)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_client(self):

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=8000)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        try:
            service = build('drive', 'v3', credentials=creds)
            return service
        except HttpError as error:
            self.logger.error(f'An error occurred: {error}')
            raise error

    def share_document(self, file_id, email):
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        command = self.client.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
        )
        command.execute()


Client('random', 'randomm').share_document(link, mail)

