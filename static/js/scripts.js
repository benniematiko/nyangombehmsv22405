document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.querySelector(".sidebar");
    if (!sidebar) return;

    const currentPath = window.location.pathname;

    // -----------------------------------------------------------------------
    // 1. SET ACTIVE STATE ON PAGE LOAD
    // -----------------------------------------------------------------------
    sidebar.querySelectorAll(".sidebar-menu a").forEach(link => {

        const href = link.getAttribute("href");
        if (!href || href === "" || href === "#") return;

        let linkPath;
        try {
            linkPath = new URL(link.href).pathname;
        } catch {
            return;
        }

        const prefix        = link.dataset.prefix;
        const isExactMatch  = currentPath === linkPath;
        const isPrefixMatch = prefix && currentPath.startsWith(prefix);

        if (isExactMatch || isPrefixMatch) {
            link.classList.add("active");

            const parentSubmenu = link.closest(".has-submenu");
            if (parentSubmenu) {
                parentSubmenu.classList.add("submenu-open");
            }
        }
    });

    // -----------------------------------------------------------------------
    // 2. ACCORDION TOGGLE — delegated listener, single source of truth
    // -----------------------------------------------------------------------
    sidebar.addEventListener("click", (e) => {
        const trigger = e.target.closest(".submenu-trigger");
        if (!trigger) return;

        e.preventDefault();
        e.stopPropagation();

        const parentLi = trigger.closest(".has-submenu");
        if (!parentLi) return;

        const isOpen = parentLi.classList.contains("submenu-open");

        sidebar.querySelectorAll(".has-submenu.submenu-open").forEach(openItem => {
            if (openItem !== parentLi) {
                openItem.classList.remove("submenu-open");
            }
        });

        parentLi.classList.toggle("submenu-open", !isOpen);
    });

});