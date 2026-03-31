/* app.js — EAPS Flask App Global JS */

// Highlight active nav link (already done server-side, this is a fallback)
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });

  // Theme Toggle Logic
  const themeToggle = document.getElementById('theme-toggle');
  const themeIcon = document.getElementById('theme-icon');
  
  if (themeToggle && themeIcon) {
    // Set initial icon
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    themeIcon.textContent = currentTheme === 'light' ? '☀️' : '🌙';
    
    themeToggle.addEventListener('click', () => {
      const theme = document.documentElement.getAttribute('data-theme');
      const newTheme = theme === 'light' ? 'dark' : 'light';
      
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('eaps_theme', newTheme);
      themeIcon.textContent = newTheme === 'light' ? '☀️' : '🌙';
    });
  }
});
