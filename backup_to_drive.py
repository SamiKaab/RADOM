import os
import os.path
import shutil
import logging
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


# Constants
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_NAME = "DataBackup"
DATA_DIR = "data"
BACKUP_DIR = "BackedUp"


def setup_logging():
    """Configure logging for the script."""
    log_file = "backup.log"
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(message)s")


def get_credentials():
    """
    Get the user credentials for Google Drive.

    Returns:
        The user credentials for Google Drive.
    """
    # Check if a token file exists and load the credentials from it if it does
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If the credentials are invalid or don't exist, obtain new credentials from the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # If the credentials have expired, refresh them
            creds.refresh(Request())
        else:
            # If the credentials don't exist or are invalid, obtain new credentials from the user
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the new credentials to a token file
        with open("token.json","w") as token:
            token.write(creds.to_json())

    # Return the user credentials
    return creds



def create_folder(service):
    """
    Create a folder named `FOLDER_NAME` on Google Drive.

    Args:
        service: The Google Drive API client service object.

    Returns:
        The ID of the created or existing folder.
    """
    # Search for an existing folder with the name `FOLDER_NAME`
    response = service.files().list(
        q=f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'",
        spaces="drive"
    ).execute()

    # If no folder exists, create a new one with the name `FOLDER_NAME`
    if not response["files"]:
        file_metadata = {
            "name": FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder"
        }
        file = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = file.get("id")
    # If a folder exists, use its ID
    else:
        folder_id = response["files"][0]["id"]

    # Return the ID of the created or existing folder
    return folder_id



def upload_file(service, filename, folder_id):
    """
    Upload a file to the Google Drive folder.

    Args:
        service: The Google Drive API client service object.
        filename: The name of the file to upload.
        folder_id: The ID of the Google Drive folder to upload the file to.
    """
    # Define the metadata for the file
    file_metadata = {"name": filename, "parents": [folder_id]}

    # Create a MediaFileUpload object for the file to be uploaded
    media = MediaFileUpload(f"{DATA_DIR}/{filename}")

    # Upload the file to the Google Drive folder
    upload_file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()

    # Log a message to indicate that the file has been backed up
    logging.info(f"Backed up file: {filename}")

    # Move the file to the backup directory
    os.rename(f"{DATA_DIR}/{filename}", f"{BACKUP_DIR}/{filename}")



def backup_files():
    """
    Backup files from the `data` directory to Google Drive.
    """
    # Get the user credentials for Google Drive
    creds = get_credentials()

    # Build the Google Drive API client with the user credentials
    service = build("drive", "v3", credentials=creds)

    # Create a folder named `FOLDER_NAME` on Google Drive
    folder_id = create_folder(service)

    # Loop over all files in the `data` directory and upload them to the Google Drive folder
    for filename in os.listdir(DATA_DIR):
        upload_file(service, filename, folder_id)



def is_internet_available():
    """Check if an internet connection is available."""
    try:
        requests.get("http://google.com")
        logging.info("Internet access available")
        return True
    except requests.exceptions.ConnectionError:
        logging.error("No internet access available")
        return False


if __name__ == "__main__":
    setup_logging()
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if is_internet_available():
        backup_files()
