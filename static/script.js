// Elements for dark mode
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

const mainContainerElement = document.querySelector('.main-container')

// Create footer element
const footerElement = (function () {
    const footerDiv = document.createElement('div');
    footerDiv.setAttribute('class', 'footer');


    const footerText = document.createElement('a');
    const footerTextStyles = `link-danger link-offset-2 link-offset-3-hover link-underline link-underline-opacity-0 link-underline-opacity-75-hover`
    footerText.setAttribute('href', 'https://github.com/neilcasas')
    footerText.setAttribute('class', footerTextStyles)
    footerText.textContent = 'Created by Neil Casas © 2024';
    footerDiv.appendChild(footerText);

    mainContainerElement.appendChild(footerDiv);
})();