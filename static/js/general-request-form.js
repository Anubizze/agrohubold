(function () {
    'use strict';

    var form = document.getElementById('generalRequestForm');
    if (!form) return;

    var messageBox = document.getElementById('generalRequestMessageBox');
    var fileInput = document.getElementById('generalRequestFile');
    var attachLabel = form.querySelector('.site-request__attach span');

    if (fileInput && attachLabel) {
        fileInput.addEventListener('change', function () {
            attachLabel.textContent = fileInput.files.length
                ? fileInput.files[0].name
                : attachLabel.getAttribute('data-default') || attachLabel.textContent;
        });
        attachLabel.setAttribute('data-default', attachLabel.textContent);
    }

    function showMessage(text, type) {
        if (!messageBox) return;
        messageBox.hidden = false;
        messageBox.textContent = text;
        messageBox.className = 'site-request__message is-' + type;
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        if (!form.reportValidity()) {
            return;
        }

        var submitBtn = form.querySelector('.site-request__submit');
        if (submitBtn) submitBtn.disabled = true;

        fetch(form.getAttribute('action') || '/services/general-request/', {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.success) {
                    showMessage(data.message, 'success');
                    form.reset();
                    if (attachLabel) {
                        attachLabel.textContent = attachLabel.getAttribute('data-default') || attachLabel.textContent;
                    }
                    setTimeout(function () {
                        var modalEl = document.getElementById('generalRequestModal');
                        if (modalEl) {
                            var instance = bootstrap.Modal.getInstance(modalEl);
                            if (instance) instance.hide();
                        }
                        if (messageBox) messageBox.hidden = true;
                    }, 2200);
                } else {
                    showMessage(data.message || 'Ошибка отправки', 'error');
                }
            })
            .catch(function () {
                showMessage('Произошла ошибка при отправке заявки', 'error');
            })
            .finally(function () {
                if (submitBtn) submitBtn.disabled = false;
            });
    });
})();
