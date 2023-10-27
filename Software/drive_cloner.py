import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import hashlib
from tqdm import tqdm
import json

# Define your service account credentials JSON file path
SERVICE_ACCOUNT_CREDENTIALS = 'credentials.json'

# Initialize the Google Drive API client
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_CREDENTIALS, scopes=['https://www.googleapis.com/auth/drive']
)
drive_service = build('drive', 'v3', credentials=credentials)

# Define the base directory where you want to save downloaded files
BASE_DOWNLOAD_DIR = 'DriveData'

# Function to download files recursively
def download_folder_contents(folder_id, parent_dir):
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    if not files and folder_id != 'root':
        # The folder is empty: delete it from Google Drive
        drive_service.files().delete(fileId=folder_id).execute()
    for file in files:
        file_id = file['id']
        file_name = file['name']
        mime_type = file['mimeType']

        if mime_type == 'application/vnd.google-apps.folder':
            # Create a local directory for the folder and recursively download its contents
            folder_dir = os.path.join(parent_dir, file_name)
            if not os.path.exists(folder_dir):
                os.makedirs(folder_dir)
            download_folder_contents(file_id, folder_dir)
        else:
            # check if the file already exists
            if os.path.exists(os.path.join(parent_dir, file_name)):
                print(f"File '{file_name}' already exists. Skipping.")
                #delete file from google drive
                drive_service.files().delete(fileId=file_id).execute()
            else:
                # Download and verify the file
                downloaded_file_path = os.path.join(parent_dir, file_name)
                request = drive_service.files().get_media(fileId=file_id)
                with open(downloaded_file_path, 'wb') as file:
                    download_request = MediaIoBaseDownload(
                        file, request
                    )
                    done = False
                    while not done:
                        status, done = download_request.next_chunk()
                print(f"File '{file_name}' downloaded successfully.")
                    
                # Verify the downloaded file using MD5 hash (you can use other hash algorithms)
                expected_md5 = drive_service.files().get(fileId=file_id, fields="md5Checksum").execute()['md5Checksum']
                downloaded_file_path = os.path.join(parent_dir, file_name)
                with open(downloaded_file_path, 'rb') as downloaded_file:
                    md5 = hashlib.md5(downloaded_file.read()).hexdigest()
                if md5 == expected_md5:
                    print(f"File '{file_name}' hash matches.")
                    #delete file from google drive
                    drive_service.files().delete(fileId=file_id).execute()
                else:
                    print(f"File '{file_name}' hash does not match")
                    #delete local file
                    os.remove(downloaded_file_path)

def list_all_files():
    results = drive_service.files().list(
        q="trashed=false",
        fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    if not files:
        print('No files found.')
    else:
        print('Files:')
        for file in files:
            print(f"{file['name']} ({file['id']})")
            
def list_folder_structure(service, folder_id='root'):
    """
    List the folder structure of Google Drive and return it as a JSON structure.

    Args:
    - service: The initialized Google Drive API service.
    - folder_id: The ID of the folder to start listing from (default is 'root' for the root folder).

    Returns:
    - A JSON structure representing the folder structure.
    """
    results = service.files().list(q=f"'{folder_id}' in parents", pageSize=1000).execute()
    items = results.get('files', [])

    folder_structure = []

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            subfolder = {
                'id': item['id'],
                'name': item['name'],
                'type': 'folder',
                'children': list_folder_structure(service, item['id'])  # Recursively list subfolders
            }
            folder_structure.append(subfolder)
        else:
            file = {
                'id': item['id'],
                'name': item['name'],
                'type': 'file'
            }
            folder_structure.append(file)

    return folder_structure

def pretty_print_folder_structure(folder_structure):
    """
    Pretty-print the folder structure JSON with indentation.

    Args:
    - folder_structure: The JSON structure representing the folder hierarchy.
    """
    print(json.dumps(folder_structure, indent=3))

def delete_all_files():
    # recursively delete every file and folder in the drive
    results = drive_service.files().list(
        fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    if not files:
        print('No files found.')
    else:
        for file in tqdm(files):
            drive_service.files().delete(fileId=file['id']).execute()
            print(f"File '{file['name']}' deleted successfully.")

if __name__ == '__main__':
    # # Start downloading from the root folder
    # download_folder_contents('root', BASE_DOWNLOAD_DIR)

    # print("All files and folders downloaded, verified, and cloned from Google Drive.")
    
    # # downloaded_file_path = 'DriveData\\A4A5\\data\\SKA03\\231005\\SKA03_231005_20244.csv'
    # # downloaded_size = os.path.getsize(downloaded_file_path)
    # # print(downloaded_size)
    # delete_all_files()
    folder_struct =  list_folder_structure(drive_service)
    print(folder_struct)
    pretty_print_folder_structure(folder_struct)

