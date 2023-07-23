from __future__ import print_function

import logging
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_access_share_bot.bot_logging.bot_logging import BotLoggingHandler

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


class Client:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.logger = logging.getLogger("client")
        self.setup_logger()
        self.client = self.get_client()

    def setup_logger(self):
        handler = BotLoggingHandler(self.bot, self.chat_id)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_client(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("credentials/token.json"):
            creds = Credentials.from_authorized_user_file(
                "credentials/token.json", SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8000)
            # Save the credentials for the next run
            with open("credentials/token.json", "w") as token:
                token.write(creds.to_json())
        try:
            service = build("drive", "v3", credentials=creds)
            return service
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")
            raise error

    def share_document(self, link, email):
        user_permission = {"type": "user", "role": "writer", "emailAddress": email}
        command = self.client.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields="id",
        )

        try:
            command.execute()
            self.logger.info(f"Sharing the access to {email}")
        except Exception as e:
            self.logger.error(f"Error sharing {file_id} access with {email}: {e}")
