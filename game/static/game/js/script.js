document.addEventListener("DOMContentLoaded", function () {
    let alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = "0"; // Fade out
            setTimeout(() => alert.style.display = "none", 500); // Hide after fading out
        }, 3000); // Disappear after 3 seconds
    });
});