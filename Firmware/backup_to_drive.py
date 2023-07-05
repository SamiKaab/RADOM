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
from google.oauth2 import service_account


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
    # if os.path.exists("token.json"):
    #     creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # # If the credentials are invalid or don't exist, obtain new credentials from the user
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         # If the credentials have expired, refresh them
    #         creds.refresh(Request())
    #     else:
    #         # If the credentials don't exist or are invalid, obtain new credentials from the user
    #         creds = service_account.Credentials.from_service_account_file("be-up-standing-3ef624974c8c.json", scopes=SCOPES)
    #         # flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    #         # creds = flow.run_local_server(port=0)
    #     # # Save the new credentials to a token file
    #     # with open("token.json","w") as token:
    #     #     token.write(creds.to_json())

    # # Return the user credentials
    creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

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
    print(upload_file)
    # Log a message to indicate that the file has been backed up
    logging.info(f"Backed up file: {filename}")

    # Move the file to the backup directory
    os.rename(f"{DATA_DIR}/{filename}", f"{BACKUP_DIR}/{filename}")



def backup_files(file_list):
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
    for filename in file_list:
        upload_file(service, filename, folder_id)



def is_internet_available():
    """Check if an internet connection is available."""
    try:
        requests.get("http://google.com", timeout=5)
        logging.info("Internet access available")
        return True
    except:
        logging.error("No internet access available")
        return False

def delete_all():
    # Set up the service account credentials
    credentials = get_credentials()

    # Build the Google Drive API client
    drive_service = build("drive", "v3", credentials=credentials)

    # List all files
    response = drive_service.files().list().execute()
    files = response.get("files", [])

    # Iterate through the files and delete them
    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        drive_service.files().delete(fileId=file_id).execute()
        print(f"Deleted file: {file_name}")
        
def download_all():
    credentials = get_credentials()
   # Build the Google Drive API client
    drive_service = build("drive", "v3", credentials=credentials)

    # Retrieve file metadata with parent information
    response = drive_service.files().list(fields="files(id, name, mimeType, parents)").execute()
    files = response.get("files", [])

    # Iterate through the files and download them
    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        parents = file.get("parents", [])
        mime_type = file["mimeType"]

        # Create the folder structure on the local system
        folder_path = ""
        for parent_id in parents:
            parent_response = drive_service.files().get(fileId=parent_id, fields="name").execute()
            parent_name = parent_response.get("name", "")
            folder_path = os.path.join(parent_name, folder_path)
            os.makedirs(folder_path, exist_ok=True)

        # Download the file
        if "application/vnd.google-apps" in mime_type:
            print(f"Skipping export for file: {file_name}. It is not a supported Google Docs Editors file.")
            continue

        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute()

        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "wb") as f:
            f.write(file_content)

        print(f"Downloaded file: {file_path}")

if __name__ == "__main__":
    # setup_logging()
    # os.makedirs(BACKUP_DIR, exist_ok=True)

    if is_internet_available():
        file_list = []
        for filename in os.listdir("data"):
            file_list.append(filename)
        backup_files(file_list)
        # download_all()
        # delete_all()
        # get_credentials()