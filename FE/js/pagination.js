/**
 * Pagination Utility
 * Hỗ trợ phân trang client-side cho các trang admin
 */

class Pagination {
    constructor(options) {
        this.items = options.items || [];
        this.itemsPerPage = options.itemsPerPage || 6;
        this.currentPage = 1;
        this.containerSelector = options.containerSelector;
        this.paginationSelector = options.paginationSelector;
        this.renderCallback = options.renderCallback;
    }

    /**
     * Tính tổng số trang
     */
    getTotalPages() {
        return Math.ceil(this.items.length / this.itemsPerPage);
    }

    /**
     * Lấy items cho trang hiện tại
     */
    getCurrentPageItems() {
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        return this.items.slice(startIndex, endIndex);
    }

    /**
     * Render pagination controls
     */
    renderPagination() {
        const totalPages = this.getTotalPages();
        const paginationContainer = document.querySelector(this.paginationSelector);

        if (!paginationContainer) return;

        // Nếu chỉ có 1 trang hoặc không có items, ẩn pagination
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        let paginationHTML = '<ul class="pagination justify-content-center">';

        // Nút "Trước"
        paginationHTML += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage - 1}" ${this.currentPage === 1 ? 'tabindex="-1" aria-disabled="true"' : ''}>
                    Trước
                </a>
            </li>
        `;

        // Các số trang
        const maxVisiblePages = 5; // Số trang hiển thị tối đa
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        // Điều chỉnh startPage nếu endPage đã ở cuối
        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        // Thêm trang đầu và dấu "..." nếu cần
        if (startPage > 1) {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" data-page="1">1</a>
                </li>
            `;
            if (startPage > 2) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }

        // Render các trang
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}" ${i === this.currentPage ? 'aria-current="page"' : ''}>
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        // Thêm dấu "..." và trang cuối nếu cần
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>
                </li>
            `;
        }

        // Nút "Sau"
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage + 1}" ${this.currentPage === totalPages ? 'tabindex="-1" aria-disabled="true"' : ''}>
                    Sau
                </a>
            </li>
        `;

        paginationHTML += '</ul>';
        paginationContainer.innerHTML = paginationHTML;

        // Thêm event listeners
        this.attachPaginationEvents();
    }

    /**
     * Attach click events cho pagination
     */
    attachPaginationEvents() {
        const paginationContainer = document.querySelector(this.paginationSelector);
        if (!paginationContainer) return;

        const links = paginationContainer.querySelectorAll('a.page-link');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(link.getAttribute('data-page'));
                if (page && page !== this.currentPage && page >= 1 && page <= this.getTotalPages()) {
                    this.goToPage(page);
                }
            });
        });
    }

    /**
     * Chuyển đến trang cụ thể
     */
    goToPage(page) {
        this.currentPage = page;
        this.render();
    }

    /**
     * Update items và render lại
     */
    updateItems(items) {
        this.items = items;
        this.currentPage = 1; // Reset về trang 1
        this.render();
    }

    /**
     * Render cả data và pagination
     */
    render() {
        const currentItems = this.getCurrentPageItems();

        // Gọi callback để render items
        if (this.renderCallback) {
            this.renderCallback(currentItems);
        }

        // Render pagination controls
        this.renderPagination();

        // Scroll to top (optional)
        const container = document.querySelector(this.containerSelector);
        if (container) {
            container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}
