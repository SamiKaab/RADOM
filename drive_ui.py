import sys
import os
import re
from datetime import datetime
import pytz
import io

from PySide2.QtWidgets import (
    QApplication,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QMessageBox,
    QMenu,
    QAction,
)
from PySide2.QtCore import Qt, QThread, Signal
from PySide2.QtGui import QCursor, QIcon
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
import requests



TIMEZONE = 'Australia/Brisbane'
SCOPES = ['https://www.googleapis.com/auth/drive']

def internet_available():
    """Check if an internet connection is available."""
    try:
        requests.get("http://google.com")
        return True
    except requests.exceptions.ConnectionError:
        return False

def get_credentials():
    """
    Get the user credentials for Google Drive.

    Returns:
        The user credentials for Google Drive.
    """
    # Check if a token file exists and load the credentials from it if it does
    try:
        # # Return the user credentials
        creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    except:
        creds = None
        
    return creds

def get_path(service, item_id, path=''):
    file = service.files().get(fileId=item_id, fields='id, name, parents').execute()
    name = file.get('name')
    parents = file.get('parents')
    if parents:
        parent_id = parents[0]  # Get the first parent ID
        path = get_path(service, parent_id, path)  # Recurse with the parent ID
    return os.path.join(path, name)

def sanitize_name(name):
    return re.sub(r'[*?:"<>|]', "_", name)

def manage_file(drive_service, item_id='root', action='download', output_dir='DataBackup', progress_callback=None):
    item_response = drive_service.files().get(fileId=item_id, fields="id, name, mimeType, parents").execute()
    item_name = item_response.get("name", "")
    item_mime_type = item_response.get("mimeType", "")

    if action != 'delete':
        item_path = get_path(drive_service, item_id)
        item_path = sanitize_name(item_path)
        local_path = os.path.join(output_dir, item_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

    if "application/vnd.google-apps.folder" not in item_mime_type:
        if action == 'download':
            request = drive_service.files().get_media(fileId=item_id)
            output_file = io.FileIO(local_path, 'wb')
            media_request = MediaIoBaseDownload(output_file, request)
            done = False
            progress = 0

            while not done:
                status, done = media_request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress_callback:
                        progress_callback(progress)

            output_file.close()

            if action == 'delete':
                drive_service.files().delete(fileId=item_id).execute()
                if progress_callback:
                    progress_callback(100)

        elif action == 'delete':
            drive_service.files().delete(fileId=item_id).execute()

        return

    response = drive_service.files().list(q=f"'{item_id}' in parents", fields="files(id, name, mimeType, parents)").execute()
    files = response.get("files", [])

    progress = 0

    for i,file in enumerate(files):
        progress = i/len(files)*100
        if progress_callback:
            progress_callback(progress)
        manage_file(drive_service, file['id'], action=action, output_dir=output_dir, progress_callback=progress_callback)

    if action == 'delete':
        drive_service.files().delete(fileId=item_id).execute()
        if progress_callback:
            progress_callback(100)



def list_files(service, folder_id=None):
    if folder_id:
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=1000, fields="nextPageToken, files(id,name,mimeType,size,createdTime,modifiedTime)").execute()
    else:
        results = service.files().list(
            q="'root' in parents and mimeType='application/vnd.google-apps.folder'",
            pageSize=1000, fields="nextPageToken, files(id,name,mimeType,size,createdTime,modifiedTime)").execute()

    items = results.get('files', [])
    return items

def convert_size(size_in_bytes):
    units = ['B', 'KB', 'MB', 'GB','TB']
    unit_index = 0

    while size_in_bytes >= 1024 and unit_index < len(units) - 1:
        size_in_bytes /= 1024
        unit_index += 1

    rounded_size = round(size_in_bytes, 2) if unit_index > 0 else round(size_in_bytes)
    return f"{rounded_size} {units[unit_index]}"


def convert_datetime(datetime_str):
    datetime_obj = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    utc_datetime = datetime_obj.replace(tzinfo=pytz.UTC)
    upload_tz = pytz.timezone(TIMEZONE)
    localized_datetime = utc_datetime.astimezone(upload_tz)
    formatted_datetime = localized_datetime.strftime('%d/%m/%Y %H:%M')
    return formatted_datetime

class FileExplorer(QWidget):
    def __init__(self, parent=None):
        super(FileExplorer, self).__init__(parent)
        self.setWindowTitle("Google Drive Explorer")
        self.setWindowIcon(QIcon('images//Google-Drive-Logo-700x394.png'))
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Date Modified", "Size"])#, "ID", "Type"])
        self.file_tree.header().setSectionsClickable(True)
        self.file_tree.header().sectionClicked.connect(self.sort_tree_by_column)

        self.download_button = QPushButton("Download All")
        self.refresh_button = QPushButton("Refresh")
        self.download_button.clicked.connect(self.download_all)
        self.refresh_button .clicked.connect(self.refresh)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        self.creds = get_credentials()
        try:
            self.service = build('drive', 'v3', credentials=self.creds, static_discovery=False)
        except:
            self.service = None
        layout = QVBoxLayout()
        layout.addWidget(self.file_tree)
        layout.addWidget(self.download_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        
        self.populate_tree()
            

    def refresh(self):
        self.file_tree.clear()
        self.populate_tree()

    def sort_tree_by_column(self, column):
        if column != 2:
            self.file_tree.sortItems(column, Qt.AscendingOrder)
        
    
    def populate_tree(self, parent_item=None):
        if internet_available():
            if self.service== None:
                self.service = build('drive', 'v3', credentials=self.creds, static_discovery=False)
            if parent_item is None:
                items = list_files(self.service)
                for item in items:
                    tree_item = QTreeWidgetItem(self.file_tree, [item['name'], '', ''])
                    tree_item.setData(0, Qt.UserRole, item['id'])
                    if item['mimeType'] == 'application/vnd.google-apps.folder':
                        tree_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                        tree_item.setExpanded(True)
                    self.populate_tree(tree_item)
            else:
                if parent_item.childCount() == 0:
                    parent_id = parent_item.data(0, Qt.UserRole)
                    items = list_files(self.service, parent_id)
                    for item in items:
                        tree_item = QTreeWidgetItem(parent_item, [item['name'], convert_datetime(item['modifiedTime']), convert_size(int(item['size']))])
                        tree_item.setData(0, Qt.UserRole, item['id'])
                        if item['mimeType'] == 'application/vnd.google-apps.folder':
                            tree_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                            tree_item.setExpanded(False)
                            self.populate_tree(tree_item)
        else:
            QMessageBox.warning(self, "No Internet Connection", "Please check your internet connection and try again.")
                
                

    def show_context_menu(self, point):
        # Get the item at the point
        item = self.file_tree.itemAt
        # Get the item at the point
        item = self.file_tree.itemAt(point)
        if item:
            context_menu = QMenu(self)
            
            download_action = QAction("Download")
            download_action.triggered.connect(lambda: self.download_item(item))
            delete_action = QAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_item(item))
            
            context_menu.addAction(download_action)
            context_menu.addAction(delete_action)
            
            # Show the context menu
            context_menu.exec_(self.file_tree.mapToGlobal(point))

    def download_all(self):
        if internet_available():

            dialog = QFileDialog()
            output_dir = dialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:  # If the user didn't cancel the dialog
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                self.progress_bar.setMaximum(100)
                
                self.download_thread = DownloadThread(self.service, output_dir)
                self.download_thread.progressChanged.connect(self.update_progress)
                self.download_thread.finished.connect(self.download_finished)
                
                self.download_thread.start()
        else:
            QMessageBox.warning(self, "No Internet Connection", "Please check your internet connection and try again.")
    def download_item(self, item):
        if internet_available():
            file_id = item.data(0, Qt.UserRole)

            dialog = QFileDialog()
            output_dir = dialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:  # If the user didn't cancel the dialog
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                self.progress_bar.setMaximum(100)
                
                self.download_thread = DownloadThread(self.service, output_dir, file_id)
                self.download_thread.progressChanged.connect(self.update_progress)
                self.download_thread.finished.connect(self.download_finished)
                
                self.download_thread.start()
        else:
            QMessageBox.warning(self, "No Internet Connection", "Please check your internet connection and try again.") 
            
    def delete_item(self, item):
        if internet_available():
            file_id = item.data(0, Qt.UserRole)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(100)
            
            self.delete_thread = DeleteThread(self.service, file_id)
            self.delete_thread.progressChanged.connect(self.update_progress)
            self.delete_thread.finished.connect(self.delete_finished)
            
            self.delete_thread.start()
        else:
            QMessageBox.warning(self, "No Internet Connection", "Please check your internet connection and try again.")
            
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self):
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Download", "Download completed.")

    def delete_finished(self):
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Delete", "Delete completed.")
        self.refresh()

class DownloadThread(QThread):
    progressChanged = Signal(int)

    def __init__(self, service, output_dir, file_id=None):
        QThread.__init__(self)
        self.service = service
        self.output_dir = output_dir
        self.file_id = file_id

    def run(self):
        if self.file_id:
            manage_file(self.service, self.file_id, action='download', output_dir=self.output_dir, progress_callback=self.update_progress)
        else:
            manage_file(self.service, action='download', output_dir=self.output_dir, progress_callback=self.update_progress)

    def update_progress(self, progress):
        self.progressChanged.emit(progress)

class DeleteThread(QThread):
    progressChanged = Signal(int)

    def __init__(self, service, file_id):
        QThread.__init__(self)
        self.service = service
        self.file_id = file_id

    def run(self):
        manage_file(self.service, self.file_id, action='delete', progress_callback=self.update_progress)

    def update_progress(self, progress):
        self.progressChanged.emit(progress)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.resize(400, 300)  # Set the window size to 800x600 pixels

    window.show()
    sys.exit(app.exec_())
