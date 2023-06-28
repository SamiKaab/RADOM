from collections.abc import Callable, Iterable, Mapping
from typing import Any
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,QSplashScreen
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QTimer, QCoreApplication, QThread, Qt
from PySide2.QtGui import QIcon, QPixmap
import sys
import paramiko
import time
import threading
import drive_ui
import flaskreceive_test
import config_editor_ui
import requests
import waitress
import authentification

class DashAppThread(QThread):
    def __init__(self, hostname=None):
        super().__init__()
        self.hostname = hostname
        self.sensorDataApp = None
    def run(self):
        self.sensorDataApp = flaskreceive_test.SensorDataApp(self.hostname)
        self.sensorDataApp.run()
    def quit(self):
        print("quitting")
        if self.sensorDataApp.server:
            self.sensorDataApp.hostname = None
            self.sensorDataApp.server.shutdown()
            self.sensorDataApp.server.close()
        print(self.sensorDataApp.server)
        self.terminate() 
        print("quitted")  
            
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        splash_image = QPixmap("images/standupdeskproject_logo.png")
        self.splash = QSplashScreen(splash_image, Qt.WindowStaysOnTopHint)
        self.splash.show()

        
        self.setWindowTitle("Be Up Standing - Not for comercial use, research purposes only")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('images/standup_logo.ico'))


        self.file_explorer = None
        self.ssh_client = None
        self.hostname = None
        self.username = 'root'
        self.password = None
        
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)  # Main vertical layout
        
        self.web_view = QWebEngineView(self)
        self.web_view.load("http://127.0.0.1:8050/")
        self.web_view.setZoomFactor(0.8)
        layout.addWidget(self.web_view)
        
        button_layout = QHBoxLayout()  # Horizontal layout for buttons
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect)
        button_layout.addWidget(self.connect_button)
        
        open_config_editor_button = QPushButton("Configure", self)
        open_config_editor_button.clicked.connect(self.open_config_editor)
        button_layout.addWidget(open_config_editor_button)

        self.start_stop_button = QPushButton("Stop Device", self, enabled=False)
        self.start_stop_button.clicked.connect(self.start_stop_program)
        button_layout.addWidget(self.start_stop_button)

        open_drive_button = QPushButton("Open Drive", self)
        open_drive_button.clicked.connect(self.open_drive)
        button_layout.addWidget(open_drive_button)

        layout.addLayout(button_layout)  # Add the button layout to the main layout
        
        self.dashAppThread = DashAppThread()
        self.dashAppThread.start()
        
        self.splash.close()
                
        
    def closeEvent(self,event):
        self.web_view.destroy()
        if self.dashAppThread.isRunning():
            self.dashAppThread.quit()
            self.dashAppThread.wait()
        event.accept()
        QCoreApplication.exit()  # Exit the application event loop

        
        
    def get_login(self):
        self.login_window = authentification.LoginWindow()
        self.login_window.closed.connect(lambda hostname, password, login_requested : self.set_login_info(hostname, password, login_requested))
        self.login_window.show()
    
    def set_login_info(self, hostname, password,login_requested):
        if login_requested:
            self.hostname = hostname
            self.password = password
            self.dashAppThread.sensorDataApp.hostname = hostname
            self.connect()
        

    def connect(self):
        if self.hostname is None:
            self.get_login()
        else:
            if self.ssh_client is None:
                try:
                    
                    # Connect to the device via SSH
                    ssh_client = paramiko.SSHClient()
                    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh_client.connect(self.hostname, username=self.username, password=self.password)
                    self.ssh_client =  ssh_client
                    self.connect_button.setText("Disconnect")
                    self.start_stop_button.setDisabled(False)
                    self.is_device_running()
                    QMessageBox.information(self, "Connection Successful", "Connected to device")

                except Exception as e:
                    print(f'Error: {e}')
                    self.ssh_client = None
                    self.hostname = None
                    self.password = None
                    QMessageBox.critical(self, "Connection Error", "Could not connect to device")
            else:
                self.start_stop_button.setDisabled(True)
                self.connect_button.setText("Connect")
                self.ssh_client.close()    
                self.ssh_client = None
                self.hostname = None
                self.password = None
                QMessageBox.information(self, "Connection Closed", "Disconnected from device")

    def is_device_running(self):
        if self.ssh_client is not None:
            try:
                # Execute the command to check if the program is running
                command = 'pgrep -f main'
                stdin, stdout, stderr = self.ssh_client.exec_command(command)

                # Read the output of the command
                output = stdout.read().decode().strip()

                # Check if the program is running
                if output:

                    print("Program is running.")
                    self.start_stop_button.setText("Stop Device")
                    return True
                else:
                    print("Program is not running.")
                    self.start_stop_button.setText("Start Device")
                    return False

            except Exception as e:
                print(f'Error: {e}')
                return False
        else:
            # add message box to say device is not connected
            QMessageBox.critical(self, "Error", "Device is not connected")

    def open_drive(self):
        # Function to open the drive
        print("Opening Drive...")
        self.file_explorer = drive_ui.FileExplorer()
        self.file_explorer.show()
    
    def open_config_editor(self):
        if self.ssh_client is not None:
            self.config_editor = config_editor_ui.ConfigEditor(self.hostname, self.password)
            self.config_editor.show()
        else:
            QMessageBox.critical(self, "Connection Error", "Device is not connected")
        
    def check_device_stopped(self,i):
        if i > 30:
            command = 'kill $(pgrep -f main)'
            if self.ssh_client is not None:
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
            command = 'kill -9 $(pgrep -f main)'
            if self.ssh_client is not None:
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
        # Function to check if the device has stopped
        device_running = self.is_device_running()
        if device_running:
            # If the device is still running, check again after 1 second
            i+=1
            time.sleep(1) 
            self.check_device_stopped(i)
        else:
            # If the device has stopped, enable the start/stop button
            self.start_stop_button.setDisabled(False)

    def start_stop_program(self):
        device_running = self.is_device_running()
        # Function to stop the program
        if self.ssh_client is not None: 
            if device_running:
                try:
                    # Execute the command to stop the program
                    command = 'kill -9 $(pgrep -f main)'
                    stdin, stdout, stderr = self.ssh_client.exec_command(command)
                    self.start_stop_button.setDisabled(True)
                    for i in range(30):
                        time.sleep(1)
                        stillrunning = self.is_device_running()
                        if not stillrunning:
                            break
                    self.start_stop_button.setDisabled(False)
                    return False
                except Exception as e:
                    print(f'Error: {e}')
            else:
                try:
                    # Execute the command to run the program
                    command = '/root/Firmware/shell_scripts/run_stand_up.sh'
                    stdin, stdout, stderr = self.ssh_client.exec_command(command)
                    self.start_stop_button.setDisabled(True)
                    QMessageBox.information(self, "Start up", "The device may take up to 30 seconds to start.")
                    for i in range(30):
                        time.sleep(1)
                        stillrunning = self.is_device_running()
                        if stillrunning:
                            break
                    self.start_stop_button.setDisabled(False)
                    return False
                except Exception as e:
                    print(f'Error: {e}')
        else:
            # add message box to say device is not connected
            QMessageBox.about(self, "Conncetion Error", "Device is not connected")
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
