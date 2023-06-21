from collections.abc import Callable, Iterable, Mapping
from typing import Any
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QTimer, QCoreApplication, QThread
import sys
import drive_ui
import paramiko
import time
import threading
import flaskreceive_test
import requests
import waitress
# add options to send config files to the device
# add

class DashAppThread(QThread):
    def run(self):
        self.sensorDataApp = flaskreceive_test.SensorDataApp()
        self.sensorDataApp.run()
    def quit(self):
        if self.sensorDataApp.server:
            self.sensorDataApp.server.close()
        self.terminate()   
            
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Embedded Website")
        self.setGeometry(100, 100, 800, 600)


        self.file_explorer = None
        self.ssh_client = None
        
        # Create a widget for the main layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        
        # Create a vertical box layout
        layout = QVBoxLayout(main_widget)

        # Create a web view
        self.web_view = QWebEngineView(self)
        self.web_view.load("http://127.0.0.1:8050/")  # Load a website
        self.web_view.setZoomFactor(0.8)  # Set the zoom factor to scale down the website

        # Add the web view to the layout
        layout.addWidget(self.web_view)

        # Create "Open Drive" button
        open_drive_button = QPushButton("Open Drive", self)
        open_drive_button.clicked.connect(self.open_drive)

        # Add the "Open Drive" button to the layout
        layout.addWidget(open_drive_button)

        # Create "Stop Program" button
        self.start_stop_button = QPushButton("Stop Program", self)
        self.start_stop_button.clicked.connect(self.start_stop_program)

        # Add the "Stop Program" button to the layout
        layout.addWidget(self.start_stop_button)
        
        # create the Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect)

        # Add the "Stop Program" button to the layout
        layout.addWidget(self.connect_button)
        self.onStart()
        
    def onStart(self):
        self.dashAppThread = DashAppThread()
        self.dashAppThread.start()
        
        self.connect()
        if self.ssh_client is not None:
            
            if self.is_device_running():
                self.start_stop_button.setText("Stop Device")
            else:
                self.start_stop_button.setText("Start Device")

    def closeEvent(self,event):
        self.web_view.destroy()
        if self.dashAppThread.isRunning():
            self.dashAppThread.quit()
            self.dashAppThread.wait()
        event.accept()
        
        
    def connect(self):
        if self.ssh_client is None:
            try:
                # SSH connection details
                hostname = 'omega-a17e.local'
                username = 'root'
                password = 'onioneer'

                # Connect to the device via SSH
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname, username=username, password=password)
                self.ssh_client =  ssh_client
                self.connect_button.setText("Disconnect")
                self.start_stop_button.setDisabled(False)
                self.is_device_running()

            except Exception as e:
                print(f'Error: {e}')
                self.ssh_client = None
                QMessageBox.about(self, "Error", "Could not connect to device")
        else:
            self.start_stop_button.setDisabled(True)
            self.connect_button.setText("Connect")
            self.ssh_client.close()    
            self.ssh_client = None

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
            QMessageBox.about(self, "Error", "Device is not connected")

    def open_drive(self):
        # Function to open the drive
        print("Opening Drive...")
        self.file_explorer = drive_ui.FileExplorer()
        self.file_explorer.show()
        
    def check_device_stopped(self,i):
        if i > 30:
            command = 'kill -9 $(pgrep -f main)'
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
                    command = 'kill $(pgrep -f main)'
                    stdin, stdout, stderr = self.ssh_client.exec_command(command)
                    self.start_stop_button.setDisabled(True)
                    check_thread = threading.Thread(target = self.check_device_stopped,args=(0,))
                    check_thread.start()    
                    #a thread to check that the device stopped
                    

                    return False
                except Exception as e:
                    print(f'Error: {e}')
            else:
                try:
                    # Execute the command to run the program
                    command = '/root/Firmware/run_stand_up.sh'
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
            QMessageBox.about(self, "Error", "Device is not connected")
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
