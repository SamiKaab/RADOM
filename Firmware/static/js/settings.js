// document.getElementById('configureButton').addEventListener('click', function() {
//     var overlay = document.getElementById('overlay');
//     var configFormContainer = document.getElementById('configFormContainer');
    
//     if (overlay && configFormContainer) {
//         overlay.style.display = 'block';
//         configFormContainer.style.display = 'block';
//     }
// });

document.getElementById('configureButton').addEventListener('click', function() {
    // Prompt for a password
    var password = prompt("Enter the password:");

    // Make an AJAX request to the server to check the password
    fetch('/check_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: password }),
    })
    .then(response => response.json())
    .then(data => {
        // Password is correct
        var overlay = document.getElementById('overlay');
        var configFormContainer = document.getElementById('configFormContainer');
        var elementsToExclude = ['led_intensity', 'saveButton', 'cancelButton'];

        if (overlay && configFormContainer) {
            overlay.style.display = 'block';
            configFormContainer.style.display = 'block';
        }
        if (data.valid){
            var formElements = configFormContainer.elements;
    
            document.getElementById('sampling_period').disabled = false;
            document.getElementById('write_period').disabled = false;
            document.getElementById('new_file_period').disabled = false;
            document.getElementById('upload_period').disabled = false;
            document.getElementById('id').disabled = false;
            document.getElementById('wake_at').disabled = false;
            document.getElementById('sleep_at').disabled = false;
            
        } else {
            // disable everythin inside the form except the cancel button, save button and led_intensity
            document.getElementById('sampling_period').disabled = true;
            document.getElementById('write_period').disabled = true;
            document.getElementById('new_file_period').disabled = true;
            document.getElementById('upload_period').disabled = true;
            document.getElementById('id').disabled = true;
            document.getElementById('wake_at').disabled = true;
            document.getElementById('sleep_at').disabled = true;
            // for element in configForm Container if id is not led_intensity, save button or cancel button :disable
           

            // Password is incorrect or server response indicates invalid password
            alert("Incorrect password. Access denied.");
        }
    })
    .catch(error => {
        // Handle any errors, e.g., network issues or server errors
        console.error("Error:", error);
    });
});

document.getElementById('cancelButton').addEventListener('click', function() {
    console.log('cancelButton clicked');
    event.preventDefault(); // Prevent the default button click behavior
    event.stopPropagation(); // Stop event propagation
    var overlay = document.getElementById('overlay');
    var configFormContainer = document.getElementById('configFormContainer');
    
    if (overlay && configFormContainer) {
        overlay.style.display = 'none';
        configFormContainer.style.display = 'none';
    }
});



document.getElementById('saveButton').addEventListener('click', function() {
    event.preventDefault(); // Prevent the default button click behavior
    event.stopPropagation(); // Stop event propagation
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
