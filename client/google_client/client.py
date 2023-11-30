from __future__ import print_function
import re
import logging
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_access_share_bot.utils.utils import setup_logger
from google_access_share_bot.exceptions.exceptions import _BaseException


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

#TODO create instance inside module
class GoogleClientException(_BaseException):
    pass #TODO only pass?


class GoogleClient:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)
        setup_logger(self.logger, self.bot, self.chat_id, logging.ERROR)
        self.drive_client, self.sheets_client = self.get_client()

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
            raise GoogleClientException(str(error)) from error

    #TODO update
    def share_access(self, links: list[str], email):
        """Generates the id of the document and gives the permissions to provided email"""
        batch = self.drive_client.new_batch_http_request(callback=self.callback)
        user_permission = {"type": "user", "role": "writer", "emailAddress": email}
        for link in links:
            file_id = self.generate_id(link)
            batch.add(self.drive_client.permissions().create(
                fileId=file_id,
                body=user_permission,
                fields="id")
                    )
        batch.execute()

    def get_permission_id(self, link: str, email: str) -> str | None:
        """
        Returns permission_id for document based on email

        :param link: Link to the document
        :param email: Email to search through
        :return: The ID of the permission
        """
        try:
            generated_id = self.generate_id(link)
        except GoogleClientException as e:
            self.logger.error(f"Error while generating ID: {e}")
            return None
        permissions = self.drive_client.permissions().list(
            fileId=generated_id,
            fields="permissions(id, emailAddress)"
        ).execute()
        for permission in permissions.get("permissions", []):
            if permission.get("emailAddress", "") == email:
                return permission.get("id")
        return None

    def remove_access(self, link: str, permission_id: str) -> None:
        """
        Removes permission from document

        :param link: Link to the document
        :param permission_id: The ID of the permission
        :return: None
        """
        try:
            generated_id = self.generate_id(link)
        except GoogleClientException as e:
            self.logger.error(f"Error while generating ID: {e}")
            return
        command = self.drive_client.permissions().delete(
            fileId=generated_id, permissionId=permission_id
        )
        command.execute()
        self.logger.info(f"Removed access from user")

    #TODO update with buttons
    def clean_spreadsheet(self, link):
        """
        Receives spreadsheet object using drive client.
        For each sheet of spreadsheet cleans the range in updateCells and highlights in white in repeatCell.
        All these updates are stored in requests list and send to batchUpdate function to execute at once
        """
        spreadsheet_id = self.generate_id(link)
        spreadsheet = (
            self.sheets_client.spreadsheets()
            .get(spreadsheetId=spreadsheet_id)
            .execute()
        )
        requests = []
        for sheet in spreadsheet["sheets"]:
            sheet_name = sheet.get("properties", {}).get("title")
            sheet_id = sheet.get("properties", {}).get("sheetId")
            # TODO take list names to exclude from button
            if sheet_name.lower() in ["Tasks", "Косяки", "инфа об авторах"]:
                continue

            requests.append(
                {
                    "updateCells": {
                        "range": self.get_grid_range(sheet_id, 1, 1000, 3, 26),
                        "fields": "userEnteredValue",
                    }
                }
            )

            requests.append(
                {
                    "repeatCell": {
                        "range": self.get_grid_range(sheet_id, 1, 1000, 0, 26),
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

    def callback(self, request_id, response, exception) -> None:
        """
        Callback function to handle error in each request to Google API
        :param request_id: ID of request provided or generated by user
        :param response: Response received from Google API
        :param exception: Potential error we might receive
        :return: None
        """
        if exception is not None:
            # Handle error
            self.logger.error(f"Google API batch request {request_id} failed: {exception}")
        else:
            # Handle successful response
            self.logger.info(f"Response from Google API batch request {request_id}: {response}")

    def is_google_document(self, link: str):
        """Validates that the link is a document"""
        if not isinstance(link, str):
            raise GoogleClientException("Link should be a string")
        pattern = r"(https://docs.google.com/document/d/)([a-zA-Z0-9-_]+)"
        return bool(re.match(pattern, link))

    def is_google_spreadsheet(self, link: str):
        """Validates that the link is spreadsheet"""
        if not isinstance(link, str):
            raise GoogleClientException("Link should be a string")
        pattern = r"(https://docs.google.com/spreadsheets/d/)([a-zA-Z0-9-_]+)"
        return bool(re.match(pattern, link))

    def generate_id(self, link: str) -> str:
        """Generates the id of the file from link to open the access"""
        if not isinstance(link, str):
            raise GoogleClientException("Link should be a string")
        pattern = r"(https://docs.google.com/[^/]+/d/)([a-zA-Z0-9-_]+)"
        match = re.match(pattern, link)
        if match:
            file_id = match.group(2)
            return file_id

    def get_grid_range(self, sheet_id, start_row, end_row, start_col, end_col):
        """Returns a GridRange object for batch updates."""
        return {
            "sheetId": sheet_id,
            "startRowIndex": start_row,
            "endRowIndex": end_row,
            "startColumnIndex": start_col,
            "endColumnIndex": end_col,
        }

    def is_google_email(self, email: str) -> bool:
        """
        Validates if the provided email is a Google email.

        :param email: email to validate
        :return: bool
        """
        if not isinstance(email, str):
            raise GoogleClientException("Email should be a string")
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        if not email_pattern.fullmatch(email):
            return False
        domain = email.split("@")[1].lower()
        # Check if the domain is gmail.com or your custom Google Workspace domain
        return domain in ["gmail.com", "biggiko.com", "alreadymedia.com"]