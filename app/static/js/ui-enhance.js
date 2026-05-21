(function () {
    function applyTheme(themeName) {
        var body = document.body;
        if (!body) {
            return;
        }
        if (themeName === "classic") {
            body.classList.remove("theme-modern");
        } else {
            body.classList.add("theme-modern");
        }
    }

    function initThemeToggle() {
        var saved = localStorage.getItem("workout_theme") || "modern";
        applyTheme(saved);

        var toggleBtn = document.getElementById("themeToggle");
        if (!toggleBtn) {
            return;
        }

        toggleBtn.textContent = saved === "modern" ? "Switch to Classic" : "Switch to Modern";
        toggleBtn.addEventListener("click", function () {
            var next = document.body.classList.contains("theme-modern") ? "classic" : "modern";
            localStorage.setItem("workout_theme", next);
            applyTheme(next);
            toggleBtn.textContent = next === "modern" ? "Switch to Classic" : "Switch to Modern";
        });
    }

    function initQuickFilter() {
        var input = document.querySelector("[data-ui-filter]");
        if (!input) {
            return;
        }

        var targetSelector = input.getAttribute("data-ui-filter") || ".ui-filter-item";
        var emptyNode = document.querySelector(".ui-empty");

        input.addEventListener("input", function () {
            var keyword = (input.value || "").toLowerCase().trim();
            var items = document.querySelectorAll(targetSelector);
            var visible = 0;

            items.forEach(function (item) {
                var haystack = (item.getAttribute("data-search") || item.textContent || "").toLowerCase();
                var show = !keyword || haystack.indexOf(keyword) !== -1;
                item.style.display = show ? "" : "none";
                if (show) {
                    visible += 1;
                }
            });

            if (emptyNode) {
                emptyNode.style.display = visible === 0 ? "block" : "none";
            }

            updateVisibleCounts();
        });
    }

    function initSortControls() {
        var sortNodes = document.querySelectorAll("[data-ui-sort]");
        sortNodes.forEach(function (node) {
            var targetSelector = node.getAttribute("data-ui-target") || ".ui-filter-item";

            node.addEventListener("change", function () {
                var mode = node.value;
                var items = Array.from(document.querySelectorAll(targetSelector));
                if (!items.length) {
                    return;
                }

                items.sort(function (a, b) {
                    var aName = (a.getAttribute("data-sort-name") || "").toLowerCase();
                    var bName = (b.getAttribute("data-sort-name") || "").toLowerCase();
                    var aTime = Date.parse(a.getAttribute("data-sort-time") || "") || 0;
                    var bTime = Date.parse(b.getAttribute("data-sort-time") || "") || 0;

                    if (mode === "name-desc") {
                        return bName.localeCompare(aName);
                    }
                    if (mode === "time-asc") {
                        return aTime - bTime;
                    }
                    if (mode === "time-desc") {
                        return bTime - aTime;
                    }
                    return aName.localeCompare(bName);
                });

                var parent = items[0].parentNode;
                items.forEach(function (item) {
                    parent.appendChild(item);
                });
                updateVisibleCounts();
            });
        });
    }

    function initFilterReset() {
        var resetNodes = document.querySelectorAll("[data-ui-reset-filter]");
        resetNodes.forEach(function (node) {
            node.addEventListener("click", function () {
                var input = document.querySelector("[data-ui-filter]");
                if (!input) {
                    return;
                }
                input.value = "";
                input.dispatchEvent(new Event("input"));
            });
        });
    }

    function initDensityToggle() {
        var toggleNodes = document.querySelectorAll("[data-ui-density-target]");
        toggleNodes.forEach(function (node) {
            var target = document.querySelector(node.getAttribute("data-ui-density-target"));
            if (!target) {
                return;
            }
            node.addEventListener("click", function () {
                target.classList.toggle("ui-compact");
            });
        });
    }

    function initKeyboardShortcuts() {
        window.addEventListener("keydown", function (event) {
            var input = document.querySelector("[data-ui-filter]");
            if (!input) {
                return;
            }

            if (event.key === "/" && document.activeElement !== input) {
                event.preventDefault();
                input.focus();
                input.select();
            }

            if (event.key === "Escape" && document.activeElement === input) {
                input.value = "";
                input.dispatchEvent(new Event("input"));
                input.blur();
            }
        });
    }

    function initRevealEffects() {
        if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            return;
        }

        var cards = document.querySelectorAll(".card.ui-filter-item, .ui-filter-item");
        cards.forEach(function (card, index) {
            card.classList.add("ui-reveal");
            card.style.animationDelay = String(Math.min(index * 60, 480)) + "ms";
        });
    }

    function initCountBadges() {
        var counterNodes = document.querySelectorAll("[data-ui-count]");
        counterNodes.forEach(function (node) {
            var selector = node.getAttribute("data-ui-count");
            if (!selector) {
                return;
            }
            node.textContent = document.querySelectorAll(selector).length;
        });
    }

    function updateVisibleCounts() {
        var visibleNodes = document.querySelectorAll("[data-ui-visible-count]");
        visibleNodes.forEach(function (node) {
            var selector = node.getAttribute("data-ui-visible-count");
            if (!selector) {
                return;
            }
            var count = 0;
            document.querySelectorAll(selector).forEach(function (item) {
                if (item.style.display !== "none") {
                    count += 1;
                }
            });
            node.textContent = String(count);
        });
    }

    window.addEventListener("DOMContentLoaded", function () {
        initThemeToggle();
        initQuickFilter();
        initSortControls();
        initFilterReset();
        initDensityToggle();
        initKeyboardShortcuts();
        initRevealEffects();
        initCountBadges();
        updateVisibleCounts();
    });
})();
