/* app.js — EAPS Flask App Global JS */

// Highlight active nav link (already done server-side, this is a fallback)
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
});
