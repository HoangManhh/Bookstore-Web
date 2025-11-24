// js/include.js

document.addEventListener("DOMContentLoaded", function() {
    
    // Tải Navbar
    fetch('_navbar.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('navbar-placeholder').innerHTML = data;
        });

    // Tải Footer
    fetch('_footer.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('footer-placeholder').innerHTML = data;
        });

});