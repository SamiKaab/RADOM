import subprocess

def get_wifi_name():
    # Run the command to get the Wi-Fi network details
    result = subprocess.run(['netsh', 'wlan', 'show', 'interface'], capture_output=True, text=True)

    # Get the output of the command
    output = result.stdout

    # Find the SSID in the output
    start_index = output.find("SSID")
    end_index = output.find("\n", start_index)
    ssid_line = output[start_index:end_index]
    # Extract the SSID value
    ssid = None if ssid_line == "" else ssid_line.split(":")[1].strip()

    # Print the SSID
    return ssid