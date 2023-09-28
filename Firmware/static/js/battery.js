

function updateBatteryLevel() {
    // get battery level
    fetch('/get_battery', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })

        .then((response) => response.json())    
        .then((data) => {
            const level = data.battery_level;
            const batteryLevelElement = document.getElementById('battery-level');
            const batteryTextElement = document.getElementById('battery-text');
        
            batteryLevelElement.style.width = level + '%';
            batteryTextElement.innerText = level + '%';
            // change batteryLevel color
            if (level < 20) {
                batteryLevelElement.style.backgroundColor = 'red';
            } else if (level < 50) {
                batteryLevelElement.style.backgroundColor = 'orange';
            } else {
                batteryLevelElement.style.backgroundColor = 'green';
            }
        });
        
}

// update battery level every 5 seconds
setInterval(updateBatteryLevel, 5000);

