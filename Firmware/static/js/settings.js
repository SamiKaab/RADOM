document.getElementById('settings-button').addEventListener('click', function() {
    var overlay = document.getElementById('overlay');
    var configFormContainer = document.getElementById('configFormContainer');
    var wifiSettings = document.getElementById('wifiSettings');
    var deviceSettings = document.getElementById('deviceSettings');
    var passwordSettings = document.getElementById('passwordSettings');

    if (overlay && configFormContainer) {
        overlay.style.display = 'flex';
        configFormContainer.style.display = 'flex';
    }
    if (wifiSettings) {
        wifiSettings.style.display = 'none';
        document.getElementById('WifiSettingsBtn').classList.remove('active');


    }
    if (passwordSettings) {
        passwordSettings.style.display = 'none';
        document.getElementById('PasswordSettingsBtn').classList.remove('active');

    }
    if (deviceSettings) {
        deviceSettings.style.display = 'block';
        //change DeviceSettingsBtn to active
        document.getElementById('DeviceSettingsBtn').classList.add('active');
    }
});



document.getElementById('WifiSettingsBtn').addEventListener('click', function() {
    event.preventDefault(); // Prevent the default button click behavior
    event.stopPropagation(); // Stop event propagation
    var wifiSettings = document.getElementById('wifiSettings');
    var deviceSettings = document.getElementById('deviceSettings');
    var passwordSettings = document.getElementById('passwordSettings');
    if (wifiSettings) {
        wifiSettings.style.display = 'block';
        document.getElementById('WifiSettingsBtn').classList.add('active');
        fetch('/wifi_settings', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            var networks = data.networks;
            var wifiList = document.getElementById('wifiList');
            var html = '';
            for (var i = 0; i < networks.length; i++) {
                var network = networks[i];
                html += '<li>' + network.ssid + ' (' + network.encryption + ') <button class="button" onclick="confirmAndRemove(\'' + network.ssid + '\')">Remove</button></li>';
            }
            wifiList.innerHTML = html;
        })
    }
    if (deviceSettings) {
        deviceSettings.style.display = 'none';
        document.getElementById('DeviceSettingsBtn').classList.remove('active');
    }
    if (passwordSettings) {
        passwordSettings.style.display = 'none';
        document.getElementById('PasswordSettingsBtn').classList.remove('active');
    }
});

document.getElementById('DeviceSettingsBtn').addEventListener('click', function() {
    event.preventDefault(); // Prevent the default button click behavior
    event.stopPropagation(); // Stop event propagation
    var wifiSettings = document.getElementById('wifiSettings');
    var deviceSettings = document.getElementById('deviceSettings');
    var passwordSettings = document.getElementById('passwordSettings');
    if (wifiSettings) {
        wifiSettings.style.display = 'none';
        document.getElementById('WifiSettingsBtn').classList.remove('active');
    }
    if (deviceSettings) {
        deviceSettings.style.display = 'block';
        document.getElementById('DeviceSettingsBtn').classList.add('active');
    }
    if (passwordSettings) {
        passwordSettings.style.display = 'none';
        document.getElementById('PasswordSettingsBtn').classList.remove('active');
    }
});

document.getElementById('PasswordSettingsBtn').addEventListener('click', function() {
    event.preventDefault(); // Prevent the default button click behavior
    event.stopPropagation(); // Stop event propagation
    var wifiSettings = document.getElementById('wifiSettings');
    var deviceSettings = document.getElementById('deviceSettings');
    var passwordSettings = document.getElementById('passwordSettings');

    if (wifiSettings) {
        wifiSettings.style.display = 'none';
        document.getElementById('WifiSettingsBtn').classList.remove('active');
    }
    if (deviceSettings) {
        deviceSettings.style.display = 'none';
        document.getElementById('DeviceSettingsBtn').classList.remove('active');
    }
    if (passwordSettings) {
        passwordSettings.style.display = 'block';
        document.getElementById('PasswordSettingsBtn').classList.add('active');
    }
});
function confirmAndRemove(ssid) {
    event.preventDefault();
    event.stopPropagation();
    // Use a confirmation dialog to confirm the removal
    if (confirm(`Are you sure you want to remove network "${ssid}"?`)) {
        // Make an AJAX request to remove the network
        fetch(`/remove/${ssid}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(`Network "${ssid}" has been removed.`);
                location.reload();
            } else {
                alert(`Failed to remove network "${ssid}": ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const advancedSettingsToggle = document.getElementById("advancedSettingsToggle");
    const advancedSettings = document.getElementById("advancedSettings");

    advancedSettingsToggle.addEventListener("click", function () {
        advancedSettings.classList.toggle("open");
        advancedSettingsToggle.classList.toggle("open");

    });
});

// handle the cancel button click event
// document.getElementById('cancelButton').addEventListener('click', function() {
//     console.log('cancelButton clicked');
//     event.preventDefault(); // Prevent the default button click behavior
//     event.stopPropagation(); // Stop event propagation
//     var overlay = document.getElementById('overlay');
//     var configFormContainer = document.getElementById('configFormContainer');
    
//     if (overlay && configFormContainer) {
//         overlay.style.display = 'none';
//         configFormContainer.style.display = 'none';
//     }
// });



document.getElementById('saveButton').addEventListener('click', function() {
    event.preventDefault(); // Prevent the default button click behavior
    event.stopPropagation(); // Stop event propagation
    var error = false;
    //check if sampling_period is empty
    if (document.getElementById('sampling_period').value == "") {
        error = true;
        highlightPasswordField("sampling_period");
    }

    //check if write_period is empty
    if (document.getElementById('write_period').value == "") {
        error = true;
        highlightPasswordField("write_period");
    }
    //check if new_file_period is empty
    if (document.getElementById('new_file_period').value == "") {
        error = true;
        highlightPasswordField("new_file_period");
    }
    //check if upload_period is empty
    if (document.getElementById('upload_period').value == "") {
        error = true;
        highlightPasswordField("upload_period");
    }
    //check if id is empty
    if (document.getElementById('id').value == "") {
        error = true;
        highlightPasswordField("id");
    }
    if (error) {
        return;
    }

    // Collect form data into a JavaScript object
    var formData = {
        sampling_period: document.getElementById('sampling_period').value,
        write_period: document.getElementById('write_period').value,
        new_file_period: document.getElementById('new_file_period').value,
        upload_period: document.getElementById('upload_period').value,
        id: document.getElementById('id').value,
        wake_at: document.getElementById('wake_at').value,
        sleep_at: document.getElementById('sleep_at').value,
        led_intensity: document.getElementById('led_intensity').value
    };
    
    // Generate JSON data from the form data
    var jsonData = JSON.stringify(formData, null, 2);
    console.log(jsonData);  
    // send data to /save_config' endpoint using a POST request
    fetch('/save_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: jsonData,
    });

    // Hide the overlay and form container after submission
    var overlay = document.getElementById('overlay');
    var configFormContainer = document.getElementById('configFormContainer');
    
    if (overlay && configFormContainer) {
        overlay.style.display = 'none';
        configFormContainer.style.display = 'none';
    }
});

function highlightPasswordField(id) {
    //rapidly highlight wifiPassword field on and off at 0.1s intervals for 1 seconds
    var i = 0;
    var interval = setInterval(function () {
        if (i % 2 == 0) {
            document.getElementById(id).style.border = "2px solid red";
            document.getElementById(id).style.borderRadius = "5px";
        } else {
            document.getElementById(id).style.border = "1px solid #ccc";
        }
        i++;
        if (i == 5) {
            // the border should be rounded
            document.getElementById(id).style.border = "1px solid #ccc";
            document.getElementById(id).style.borderRadius = "5px";
            clearInterval(interval);
        }
    }, 200);
}
document.getElementById("addWifiBtn").onclick = function () {
    event.preventDefault();
    event.stopPropagation();
    var error = false;
    //check if wifiPassword is empty
    if (document.getElementById("wifiPassword").value == "") {
        error = true;
        highlightPasswordField("wifiPassword");
    }

    //check if ssid is empty
    if (document.getElementById("ssid").value == "") {
        error = true;
        highlightPasswordField("ssid");
    }
    if (error) {
        return;
    }
    var formData = {
        ssid: document.getElementById("ssid").value,
        encryption: document.getElementById("encryption").value,
        wifiPassword: document.getElementById("wifiPassword").value
    }
    var jsondata = JSON.stringify(formData)
    fetch('/add_wifi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsondata,
    })  
    .then(response => response.json())
    .then(data => {
        if (data.status == "success") {
            alert("Network added successfully");
            location.reload();
        } else {
            alert("Error adding network: " + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};


document.getElementById("chgPswdBtn").onclick = function () {
    event.preventDefault();
    event.stopPropagation();
    var oldPassword = document.getElementById("oldPassword").value;
    var newPassword = document.getElementById("newPassword").value;
    var confirmPassword = document.getElementById("confirmPassword").value;
    var error = false;
    if (oldPassword == ""){
        highlightPasswordField("oldPassword");
        error = true;
    }
    
    if (newPassword == ""){
        highlightPasswordField("newPassword");
        error = true;
    }
    if (confirmPassword == "" || newPassword != confirmPassword){
        highlightPasswordField("confirmPassword");
        alert("New password and confirm password do not match");
        error = true;
    }
    //check that the password is at least 8 characters long and only contains letters and numbers
    if (newPassword.length < 8 || !newPassword.match(/^[0-9a-zA-Z]+$/)) {
        highlightPasswordField("newPassword");
        highlightPasswordField("confirmPassword");
        alert("Password must be at least 8 characters long and only contain letters and numbers");
        error = true;
    }
    if (error) {
        return;
    }
    var formData = {
        oldPassword: oldPassword,
        newPassword: newPassword
    }
    var jsondata = JSON.stringify(formData)
    fetch('/change_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsondata,
    })  
    .then(response => response.json())
    .then(data => {
        if (data.status == "success") {
            alert("Password changed successfully");
            location.reload();
        } else {
            alert("Error changing password: " + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
