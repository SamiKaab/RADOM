function setBtnStatus(){
    var deviceStatusElement = document.getElementById('device-status')
    if (deviceStatusElement.textContent == "Not Recording"){
        document.querySelector('[data-action="start"]').classList.remove('disabled');
        document.querySelector('[data-action="stop"]').classList.add('disabled');
    } else {
        document.querySelector('[data-action="start"]').classList.add('disabled');
        document.querySelector('[data-action="stop"]').classList.remove('disabled');
    }
}
setInterval(setBtnStatus, 5000);
// Add a click event listener to all buttons with the 'button' class
document.querySelectorAll('.button').forEach(function(button) {
    button.addEventListener('click', function() {
        // Get the 'data-action' attribute value
        var action = this.getAttribute('data-action');

        // Send an AJAX request to the Flask server with the action
        fetch('/button_click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action }), // Send the action value
        });

        // Add the "disabled" class to the clicked button
        this.classList.add('disabled');

        // Remove the "disabled" class from the other button
        var otherButton = action === 'start' ? document.querySelector('[data-action="stop"]') : document.querySelector('[data-action="start"]');
        otherButton.classList.remove('disabled')
    });
});