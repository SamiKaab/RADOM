import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 150)
        
        self.id = None
        self.passwd = None

        # Create widgets
        self.id_label = QLabel("ID:", self)
        self.id_input = QLineEdit(self)
        self.password_label = QLabel("Password:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login", self)

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        # Create central widget and set the layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect button click event to the login function
        self.login_button.clicked.connect(self.login)

    def login(self):
        user_id = self.id_input.text()
        password = self.password_input.text()

        if len(user_id) != 4:
            QMessageBox.warning(self, "Invalid ID", "Please enter a 4-character ID.\nThe ID should be the last four characters of the device WiFi network name.")
        elif len(password) < 1:
            QMessageBox.warning(self, "Invalid password", "Please enter the you password.")
        else:
            self.id = user_id
            self.passwd = password


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
