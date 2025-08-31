// static/js/sidebar.js - Управление sidebar на мобильных устройствах

document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.sidebar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const mainContent = document.querySelector('.main-content');

    // Переключение sidebar на мобильных устройствах
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar?.classList.toggle('show');

                // Добавляем overlay для закрытия sidebar при клике вне его
                if (sidebar?.classList.contains('show')) {
                    createOverlay();
                } else {
                    removeOverlay();
                }
            }
        });
    }

    // Создание overlay
    function createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1045;
            display: block;
            backdrop-filter: blur(2px);
        `;

        // Закрытие при клике на overlay
        overlay.addEventListener('click', function () {
            sidebar?.classList.remove('show');
            removeOverlay();
        });

        document.body.appendChild(overlay);

        // Предотвращаем прокрутку фона
        document.body.style.overflow = 'hidden';
    }

    // Удаление overlay
    function removeOverlay() {
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) {
            overlay.remove();
        }
        // Возвращаем прокрутку
        document.body.style.overflow = '';
    }

    // Закрытие sidebar при изменении размера окна
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            sidebar?.classList.remove('show');
            removeOverlay();
        }
    });

    // Закрытие sidebar при клике на ссылки на мобильных
    const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar?.classList.remove('show');
                removeOverlay();
            }
        });
    });

    // Подсветка активной ссылки
    const currentPath = window.location.pathname;
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Плавная прокрутка к началу при клике на логотип
    const brandLink = document.querySelector('.modern-brand');
    if (brandLink) {
        brandLink.addEventListener('click', function (e) {
            if (this.getAttribute('href') === window.location.pathname) {
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }
        });
    }
});