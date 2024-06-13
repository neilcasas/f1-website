const rootElement = document.documentElement;
const darkModeBtn = document.querySelector('#toggle-theme-btn');

// Function to toggle theme and save preference to local storage
function toggleTheme() {
    const currentTheme = rootElement.getAttribute('data-bs-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    rootElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme); // Save theme preference to local storage
}

// Event listener to toggle theme when button is clicked
darkModeBtn.addEventListener('click', toggleTheme);

// Retrieve theme preference from local storage on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        rootElement.setAttribute('data-bs-theme', savedTheme);
    }
});
