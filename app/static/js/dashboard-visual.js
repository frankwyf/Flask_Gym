(function () {
    function animateMetric(node, delay) {
        var target = Number(node.getAttribute("data-target") || "0");
        if (!target) {
            return;
        }

        var duration = 1100;
        var start = null;

        function tick(timestamp) {
            if (start === null) {
                start = timestamp + delay;
            }
            if (timestamp < start) {
                window.requestAnimationFrame(tick);
                return;
            }

            var progress = Math.min((timestamp - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            node.textContent = String(Math.round(target * eased));

            if (progress < 1) {
                window.requestAnimationFrame(tick);
            }
        }

        window.requestAnimationFrame(tick);
    }

    function initStageMetrics() {
        if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            return;
        }

        var values = document.querySelectorAll(".stage-value[data-target]");
        values.forEach(function (node, index) {
            animateMetric(node, Math.min(index * 140, 420));
        });
    }

    function initStageCards() {
        var cards = document.querySelectorAll("[data-stage-card]");
        cards.forEach(function (card, index) {
            card.style.animation = "ui-fade-in 520ms ease forwards";
            card.style.animationDelay = String(Math.min(index * 90, 250)) + "ms";
        });
    }

    window.addEventListener("DOMContentLoaded", function () {
        initStageMetrics();
        initStageCards();
    });
})();
