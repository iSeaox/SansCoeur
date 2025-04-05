const stickyBtn = document.getElementById('sticky-btn');
const stickyMenu = document.getElementById('sticky-menu');

stickyBtn.addEventListener('click', () => {
    stickyMenu.classList.toggle('show');
});