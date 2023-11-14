from __future__ import print_function

import logging
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_access_share_bot.bot_logging.admin_logging import \
    BotAdminLoggingHandler
from google_access_share_bot.google_client.utils import generate_id, get_grid_range

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


class GoogleClient:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.logger = logging.getLogger("google_logger")
        self.setup_logger()
        self.drive_client, self.sheets_client = self.get_client()

    def setup_logger(self):
        handler = BotAdminLoggingHandler(self.bot, self.chat_id)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%y-%m-%d"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_client(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("google_client/token.json"):
            creds = Credentials.from_authorized_user_file(
                "google_client/token.json", SCOPES
            )
        # If there are no (valid) google_client available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "google_client/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8000)
            # Save the google_client for the next run
            with open("google_client/token.json", "w") as token:
                token.write(creds.to_json())
        try:
            drive_service = build("drive", "v3", credentials=creds)
            sheets_service = build("sheets", "v4", credentials=creds)
            return drive_service, sheets_service
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")
            raise error

    def share_access(self, link, email):
        """Generates the id of the document and gives the permissions to provided email"""
        user_permission = {"type": "user", "role": "writer", "emailAddress": email}
        file_id = generate_id(link)
        command = self.drive_client.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields="id",
        )
        try:
            command.execute()
            self.logger.info(f"Sharing the {link} to {email}")
        except Exception as e:
            self.logger.error(f"Error sharing {link} access with {email}: {e}")

    def clean_spreadsheet(self, link):
        """
        Receives spreadsheet object using drive client.
        For each sheet of spreadsheet cleans the range in updateCells and highlights in white in repeatCell.
        All these updates are stored in requests list and send to batchUpdate function to execute at once
        """
        spreadsheet_id = generate_id(link)
        spreadsheet = (
            self.sheets_client.spreadsheets()
            .get(spreadsheetId=spreadsheet_id)
            .execute()
        )
        requests = []
        for sheet in spreadsheet["sheets"]:
            sheet_name = sheet.get("properties", {}).get("title")
            sheet_id = sheet.get("properties", {}).get("sheetId")
            # TODO take list names to exclude from .env
            if sheet_name.lower() in ["Tasks", "Косяки", "инфа об авторах"]:
                continue

            requests.append(
                {
                    "updateCells": {
                        "range": get_grid_range(sheet_id, 1, 1000, 3, 26),
                        "fields": "userEnteredValue",
                    }
                }
            )

            requests.append(
                {
                    "repeatCell": {
                        "range": get_grid_range(sheet_id, 1, 1000, 0, 26),
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 1.0,
                                    "green": 1.0,
                                    "blue": 1.0,
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor)",
                    }
                }
            )
        if requests:
            body = {"requests": requests}
            response = (
                self.sheets_client.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                .execute()
            )
            return response
