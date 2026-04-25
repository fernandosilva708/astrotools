/*
    Editorial by HTML5 UP (JS Logic)
*/

(function() {
    "use strict";

    document.addEventListener('DOMContentLoaded', function() {
        const sidebar = document.getElementById('sidebar');
        const toggle = document.querySelector('.sidebar-toggle');
        
        if (toggle && sidebar) {
            toggle.addEventListener('click', function() {
                sidebar.classList.toggle('visible');
            });
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (window.innerWidth <= 980) {
                const isClickInsideSidebar = sidebar.contains(event.target);
                const isClickOnToggle = toggle.contains(event.target);

                if (!isClickInsideSidebar && !isClickOnToggle && sidebar.classList.contains('visible')) {
                    sidebar.classList.remove('visible');
                }
            }
        });
    });

})();
