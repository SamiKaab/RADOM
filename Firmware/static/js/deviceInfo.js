// Function to fetch and update the device ID
function updateDeviceInfo() {
    const loader = document.getElementById("loadingDiv");
    const overlay = document.getElementById('overlay');
    fetch('/get_device_info', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        // Check if the ID has changed
        var currentDeviceID = document.getElementById('device-id').textContent;
        if (data.ID && data.ID !== currentDeviceID) {
            document.getElementById('device-id').textContent = data.ID;
        }
        var currentDeviceID = document.getElementById('device-sampling-period').textContent;
        if (data.SP && data.SP + ' s' !== currentDeviceID) {
            // Update the sampling period and add the 's' unit
            document.getElementById('device-sampling-period').textContent = data.SP + ' s';
        }
        var currentWakeAt = document.getElementById('device-wake-at').textContent;
        if (data.WAKE_AT && data.WAKE_AT !== currentWakeAt) {
            document.getElementById('device-wake-at').textContent = data.WAKE_AT;
        }
        var currentSleepAt = document.getElementById('device-sleep-at').textContent;
        if (data.SLEEP_AT && data.SLEEP_AT !== currentSleepAt) {
            document.getElementById('device-sleep-at').textContent = data.SLEEP_AT;
        }
        var currentStatus = document.getElementById('device-status').textContent;
        if (data.STATUS && data.STATUS !== currentStatus) {
            var deviceStatusElement = document.getElementById('device-status')
            deviceStatusElement.textContent = data.STATUS;
            if (data.STATUS === "Not Recording") {
                deviceStatusElement.style.color = "red";
            } 
            else if (data.STATUS === "Recording"){
                // Reset the font color to its default value for other statuses
                deviceStatusElement.style.color = "green"; // You can change this to your desired default color
            }
            else if (data.STATUS === "Uploading"){
                // Reset the font color to its default value for other statuses
                deviceStatusElement.style.color = "lightblue"; // You can change this to your desired default color
            }
            else if (data.STATUS === "Sleeping"){
                // Reset the font color to its default value for other statuses
                deviceStatusElement.style.color = "purple"; // You can change this to your desired default color
            }
            else if (data.STATUS === "Setting Up"){
                // Reset the font color to its default value for other statuses
                deviceStatusElement.style.color = "orange"; // You can change this to your desired default color
            }
            else {
                deviceStatusElement.style.color = "black"; // You can change this to your desired default color

            }

        }
        loader.style.display = "none";
        overlay.style.display = "none";
    })
    
    .catch(error => {
        loader.style.display = "block";
        overlay.style.display = "flex";
        var deviceStatusElement = document.getElementById('device-status')
        deviceStatusElement.textContent = "Restart device";
        deviceStatusElement.style.color = "black";
        console.error('Error fetching device ID:', error);
    });
}

// Fetch and update the device ID initially
updateDeviceInfo();

// Periodically check for updates (every 5 seconds in this example)
setInterval(updateDeviceInfo, 1000);
