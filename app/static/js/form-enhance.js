(function () {
    function bindValidation(formSelector) {
        var form = document.querySelector(formSelector);
        if (!form) {
            return;
        }

        form.addEventListener("submit", function (event) {
            var fields = form.querySelectorAll("input[type='text'], input[type='password']");
            var valid = true;

            fields.forEach(function (field) {
                var wrapper = field.closest("div");
                var errorNode = wrapper ? wrapper.querySelector(".error-message") : null;
                var value = (field.value || "").trim();

                if (!value) {
                    valid = false;
                    field.classList.add("ui-input-error");
                    if (errorNode) {
                        errorNode.textContent = "This field is required.";
                    }
                } else {
                    field.classList.remove("ui-input-error");
                    if (errorNode) {
                        errorNode.textContent = "";
                    }
                }
            });

            if (!valid) {
                event.preventDefault();
            }
        });
    }

    window.addEventListener("DOMContentLoaded", function () {
        bindValidation("#form");
    });
})();
