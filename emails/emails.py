import json


def get_emails_list():
    with open("emails/emails.json", "r") as f:
        data = json.load(f)
    list_of_emails = data["emails"]
    return list_of_emails
