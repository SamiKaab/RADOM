document.getElementById('configureButton').addEventListener('click', function() {
    var overlay = document.getElementById('overlay');
    var configFormContainer = document.getElementById('configFormContainer');
    
    if (overlay && configFormContainer) {
        overlay.style.display = 'block';
        configFormContainer.style.display = 'block';
    }
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
