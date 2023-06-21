import configparser
from PySide2.QtCore import QTime
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFormLayout, QTimeEdit, QWidget

class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Config Editor")

        self.config = configparser.ConfigParser()
        self.values = {
            "Sampling Period": "5",
            "Write Period": "30",
            "New File Period": "120",
            "Upload Period": "120",
            "ID": "0",
            "Wake At": "07:30",
            "Sleep At": "17:30"
        }
        self.label_to_configVar = {
            "Sampling Period": "SAMPLING_PERIOD",
            "Write Period": "WRITE_PERIOD",
            "New File Period": "NEW_FILE_PERIOD",
            "Upload Period": "UPLOAD_PERIOD",
            "ID": "ID",
            "Wake At": "WAKE_AT",
            "Sleep At": "SLEEP_AT"
        }

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QFormLayout(self.central_widget)

        self.labels = []
        self.widgets = []

        self.load_config()
        self.create_config_fields()

        self.save_button = QPushButton("Save Config")
        self.save_button.clicked.connect(self.save_config)
        self.layout.addRow("", self.save_button)

    def load_config(self):
        self.config.read("config.ini")
        if "DEFAULT" in self.config:
            for key in self.values:
                config_key = self.label_to_configVar[key]
                if config_key in self.config["DEFAULT"]:
                    self.values[key] = self.config["DEFAULT"][config_key]

    def create_config_fields(self):
        for key, value in self.values.items():
            label = QLabel(key, self)

            if key in ["Wake At", "Sleep At"]:
                time_edit = QTimeEdit(self)
                time_edit.setDisplayFormat("HH:mm")
                time_edit.setTime(QTime.fromString(value, "HH:mm"))
                time_edit.timeChanged.connect(self.update_value)

                self.widgets.append(time_edit)
                self.layout.addRow(label, time_edit)
            else:
                line_edit = QLineEdit(value, self)
                line_edit.textChanged.connect(self.update_value)

                self.widgets.append(line_edit)
                self.layout.addRow(label, line_edit)

            self.labels.append(label)

    def update_value(self, value):
        sender = self.sender()
        index = self.widgets.index(sender)
        label = self.labels[index].text()
        self.values[label] = value

    def save_config(self):
        for key, value in self.values.items():
            config_key = self.label_to_configVar[key]
            self.config["DEFAULT"][config_key] = value

        with open("config.ini", "w") as config_file:
            self.config.write(config_file)

        self.statusBar().showMessage("Config saved successfully!")


if __name__ == "__main__":
    app = QApplication([])
    window = ConfigEditor()
    window.show()
    app.exec_()
