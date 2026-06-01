(function () {
    var savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    var darkStylesheet = document.getElementById('dark-theme');
    if (savedTheme === 'dark' && darkStylesheet) {
        darkStylesheet.removeAttribute('disabled');
    }
})();

document.addEventListener('DOMContentLoaded', function () {
    var sidebarToggle = document.getElementById('sidebarToggle');
    var sidebar = document.getElementById('sidebar-wrapper');
    var backdrop = document.getElementById('sidebar-backdrop');

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('show');
        if (backdrop) backdrop.classList.remove('show');
    }

    function openSidebar() {
        if (sidebar) sidebar.classList.add('show');
        if (backdrop) backdrop.classList.add('show');
    }

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            if (sidebar.classList.contains('show')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (backdrop) {
        backdrop.addEventListener('click', closeSidebar);
    }

    var themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        var currentTheme = localStorage.getItem('theme') || 'light';
        themeToggle.checked = currentTheme === 'dark';

        themeToggle.addEventListener('change', function () {
            var newTheme = this.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            var ds = document.getElementById('dark-theme');
            if (ds) {
                if (newTheme === 'dark') {
                    ds.removeAttribute('disabled');
                } else {
                    ds.setAttribute('disabled', 'true');
                }
            }
        });
    }
});
