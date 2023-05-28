import re


def is_valid_link(link):
    pattern = r"(https://docs.google.com/document/d/)([a-zA-Z0-9-_]+)"
    match = re.match(pattern, link)
    if match:
        file_id = match.group(2)
        return file_id
    else:
        return None
