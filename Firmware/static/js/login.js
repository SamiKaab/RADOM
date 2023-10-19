const normalUserButton = document.getElementById("normal-user-btn");
normalUserButton.addEventListener("click", () => {
    window.location.href = "/dashboard/guest";
});

// JavaScript to show the admin overlay when the "Admin" button is clicked
const adminButton = document.getElementById("admin-access-btn");
const adminOverlay = document.getElementById("admin-overlay");
const submitPasswordButton = document.getElementById("password-button");
const cancelPasswordButton = document.getElementById("cancel-button");

adminButton.addEventListener("click", () => {
    fetch('/session',{
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.user_role === "admin") {
            // User is already logged in as admin, perform redirection
            window.location.href = "/dashboard/admin";
        }
        else {
            // User is not logged in as admin, show the overlay
            adminOverlay.style.display = "flex";
        }
    })
    .catch(error => {
        // Handle any errors, e.g., network issues or server errors
        console.error("Error:", error);
    });
});

cancelPasswordButton.addEventListener("click", () => {
    adminOverlay.style.display = "none";
});

submitPasswordButton.addEventListener("click", () => {
    const passwordInput = document.getElementById("admin-password").value;
    // You can add your logic to check the password here
    fetch('/check_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: passwordInput }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            // Password is correct, perform redirection
            window.location.href = data.redirect;
        } else {
            // Password is incorrect, show an alert
            alert("Incorrect password. Try again.");
        }
    })
    .catch(error => {
        // Handle any errors, e.g., network issues or server errors
        console.error("Error:", error);
    });

});


