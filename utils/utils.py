import re


def is_google_document(link):
    """Validates that the link is a document"""
    pattern = r"(https://docs.google.com/document/d/)([a-zA-Z0-9-_]+)"
    return bool(re.match(pattern, link))


def is_google_spreadsheet(link):
    """Validates that the link is spreadsheet"""
    pattern = r"(https://docs.google.com/spreadsheets/d/)([a-zA-Z0-9-_]+)"
    return bool(re.match(pattern, link))


def generate_id(link):
    """Generates the id of the file from link to open the access"""
    pattern = r"(https://docs.google.com/[^/]+/d/)([a-zA-Z0-9-_]+)"
    match = re.match(pattern, link)
    if match:
        file_id = match.group(2)
        return file_id


def get_grid_range(sheet_id, start_row, end_row, start_col, end_col):
    """Returns a GridRange object for batch updates."""
    return {
        "sheetId": sheet_id,
        "startRowIndex": start_row,
        "endRowIndex": end_row,
        "startColumnIndex": start_col,
        "endColumnIndex": end_col,
    }
