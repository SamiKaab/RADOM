# How to Set Up a Google Drive API and Obtain Credentials

The Google Drive API allows developers to programmatically interact with Google Drive to read, write, and manage files and folders. To use the API, you need to create a project in the Google Cloud Console and obtain credentials.

## Step 1: Create a Project in the Google Cloud Console

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project by clicking the project dropdown in the top navigation bar and selecting "New Project".
3. Enter a project name and click "Create".

## Step 2: Enable the Google Drive API

1. In the Google Cloud Console, navigate to your project dashboard.
2. Click the "Enable APIs and Services" button.
3. Search for "Google Drive API" and select it.
4. Click the "Enable" button.

## Step 3: Create Credentials

1. In the Google Cloud Console, navigate to the "Credentials" page.
2. Click the "Create credentials" button and select "OAuth client ID".
3. Select "Desktop app" as the application type.
4. Enter a name for the OAuth client ID and click "Create".
5. A dialog box will appear with the client ID and client secret. Click "OK" to close the dialog box.

## Step 4: Download the Credentials

1. In the Google Cloud Console, navigate to the "Credentials" page.
2. Find the "OAuth 2.0 Client IDs" section and click the download icon next to the OAuth client ID you just created.
3. Save the credentials file to a secure location on your computer.

## Step 5: Use the Credentials in Your Application

To use the credentials in your application, you can either set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the credentials file, or you can pass the credentials directly to your code.

Here's an example of how to pass the credentials to your code in Python:

```python
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file('path/to/credentials.json')
```

# Sensor Data Collection and Backup

This is a Python script for collecting sensor data from a human presence sensor and a distance sensor, and storing it in a CSV file. The data is periodically uploaded to Google Drive, and the status of the backup process is indicated using LEDs.

## Dependencies

The script uses the following libraries:

- DFRobot_mmWave
- PiicoDev_VL53L1X
- SDL_DS3231
- requests
- RPi.GPIO
- threading
- queue
- configparser
- csv

## Usage

1. Clone the repository to your Raspberry Pi
2. Install the required libraries using pip:
```pip install -r requirements.txt```

3. Configure the script using the `config.ini` file:
- `SAMPLING_PERIOD`: The sampling period in seconds (default: 1)
- `WRITE_PERIOD`: The write period in seconds (default: 60)
- `UPLOAD_PERIOD`: The upload period in seconds (default: 600)
- `ID`: The ID of the device (default: 0)
4. Run the script:
```python main.py```

