document.addEventListener("DOMContentLoaded", () => {

    const currentPath = window.location.pathname;

    // -----------------------------------------------------------------------
    // 1. SET ACTIVE STATE ON PAGE LOAD
    // Runs once on every page load and marks the correct sidebar link active.
    // -----------------------------------------------------------------------
    document.querySelectorAll(".sidebar-menu a").forEach(link => {

        const href = link.getAttribute("href");

        // Skip unbuilt links, hash-only links, and submenu triggers
        if (!href || href === "" || href === "#") return;

        let linkPath;
        try {
            linkPath = new URL(link.href).pathname;
        } catch {
            return; // skip malformed hrefs
        }

        const prefix       = link.dataset.prefix; // e.g. data-prefix="/pharmacy/"
        const isExactMatch = currentPath === linkPath;
        const isPrefixMatch = prefix && currentPath.startsWith(prefix);

        if (isExactMatch || isPrefixMatch) {
            link.classList.add("active");

            // If this link lives inside a submenu, open the parent accordion
            const parentSubmenu = link.closest(".has-submenu");
            if (parentSubmenu) {
                parentSubmenu.classList.add("submenu-open");
            }
        }
    });

    // -----------------------------------------------------------------------
    // 2. ACCORDION TOGGLE — click handler for submenu triggers
    // Only runs when the user manually clicks a parent menu item.
    // -----------------------------------------------------------------------
    document.querySelectorAll(".submenu-trigger").forEach(trigger => {

        trigger.addEventListener("click", (e) => {
            e.preventDefault(); // stop the # href from jumping the page

            const parentLi = trigger.closest(".has-submenu");

            // Close every OTHER open submenu (true accordion — one open at a time)
            document.querySelectorAll(".has-submenu.submenu-open").forEach(openItem => {
                if (openItem !== parentLi) {
                    openItem.classList.remove("submenu-open");
                }
            });

            // Toggle this one open/closed
            parentLi.classList.toggle("submenu-open");
        });
    });

});