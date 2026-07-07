// main.js - general site behaviour

document.addEventListener("DOMContentLoaded", () => {
    // Auto-hide flash messages after 4 seconds
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach((el) => {
        setTimeout(() => {
            el.style.transition = "opacity 0.5s";
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 500);
        }, 4000);
    });
});
