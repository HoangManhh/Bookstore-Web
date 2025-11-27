// js/include.js

document.addEventListener("DOMContentLoaded", function () {

    // Tải Navbar
    fetch('_navbar.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('navbar-placeholder').innerHTML = data;

            // Fetch categories for navbar
            fetch(`${CONFIG.API_BASE_URL}/products/categories`)
                .then(response => response.json())
                .then(categories => {
                    const navCategories = document.getElementById('navbarCategories');
                    if (navCategories) {
                        navCategories.innerHTML = '';
                        if (categories.length === 0) {
                            navCategories.innerHTML = '<li><span class="dropdown-item">Không có danh mục</span></li>';
                        } else {
                            categories.forEach(cat => {
                                const li = document.createElement('li');
                                li.innerHTML = `<a class="dropdown-item" href="category.html?id=${cat.id}">${cat.name}</a>`;
                                navCategories.appendChild(li);
                            });
                        }
                    }
                })
                .catch(error => {
                    console.error('Error loading navbar categories:', error);
                });

            // Update cart badge after navbar is loaded
            if (typeof Cart !== 'undefined') {
                Cart.updateBadge();
            }

            // Check login status and update navbar
            const token = localStorage.getItem('token');
            if (token) {
                fetch(`${CONFIG.API_BASE_URL}/users/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                    .then(response => {
                        if (response.ok) {
                            return response.json();
                        } else {
                            throw new Error('Unauthorized');
                        }
                    })
                    .then(user => {
                        // Show user section, hide guest section
                        const navGuest = document.getElementById('nav-guest');
                        const navUser = document.getElementById('nav-user');
                        const navUsername = document.getElementById('nav-username');

                        if (navGuest) navGuest.classList.add('d-none');
                        if (navUser) navUser.classList.remove('d-none');
                        if (navUsername) navUsername.textContent = user.fullname;

                        // Handle logout
                        const logoutBtn = document.getElementById('logoutBtn');
                        if (logoutBtn) {
                            logoutBtn.addEventListener('click', (e) => {
                                e.preventDefault();
                                localStorage.removeItem('token');
                                // Optional: Clear cart or keep it
                                // Cart.clear(); 
                                window.location.href = 'login.html';
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching user profile:', error);
                        // Invalid token, clear it
                        localStorage.removeItem('token');
                        if (typeof Cart !== 'undefined') {
                            Cart.updateBadge();
                        }
                    });
            }

            // Tải Footer
            fetch('_footer.html')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('footer-placeholder').innerHTML = data;
                });

        });
});