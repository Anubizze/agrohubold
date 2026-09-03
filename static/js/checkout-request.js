(function () {
    'use strict';

    var form = document.getElementById('serviceRequestCheckoutForm');
    if (!form) return;

    var idsInput = document.getElementById('checkoutServiceIds');
    var list = document.getElementById('checkoutServicesList');
    var messageBox = document.getElementById('checkoutRequestMessage');
    var companyField = document.getElementById('companyBinField');
    var attachInput = document.getElementById('checkoutAttachment');
    var attachLabel = form.querySelector('.service-request-attach span');

    function getIds() {
        try {
            return JSON.parse(idsInput.value || '[]');
        } catch (e) {
            return [];
        }
    }

    function setIds(ids) {
        idsInput.value = JSON.stringify(ids);
        if (!ids.length) {
            window.location.href = '/services/';
        }
    }

    function toggleClientTypeFields() {
        var legal = form.querySelector('input[name="client_type"][value="legal"]').checked;
        var companyInput = document.getElementById('companyBin');
        var iinField = document.getElementById('clientIinField');
        var iinInput = document.getElementById('checkoutClientIin');
        companyField.hidden = !legal;
        if (iinField) iinField.hidden = legal;
        if (companyInput) companyInput.required = legal;
        if (iinInput) iinInput.required = !legal;
    }

    form.querySelectorAll('input[name="client_type"]').forEach(function (radio) {
        radio.addEventListener('change', toggleClientTypeFields);
    });
    toggleClientTypeFields();

    if (attachInput && attachLabel) {
        attachInput.addEventListener('change', function () {
            attachLabel.textContent = attachInput.files.length
                ? attachInput.files[0].name
                : attachLabel.getAttribute('data-default') || attachLabel.textContent;
        });
        attachLabel.setAttribute('data-default', attachLabel.textContent);
    }

    function recalcTotal() {
        var total = 0;
        list.querySelectorAll('.service-request-item').forEach(function (row) {
            total += Number(row.getAttribute('data-price') || 0);
        });
        var totalEl = document.querySelector('.service-request-total strong');
        if (totalEl) totalEl.textContent = total.toLocaleString('ru-RU') + ' ₸';
    }

    if (list) {
        list.addEventListener('click', function (e) {
            var btn = e.target.closest('[data-remove-id]');
            if (!btn) return;
            var id = Number(btn.getAttribute('data-remove-id'));
            var ids = getIds().filter(function (itemId) { return itemId !== id; });
            setIds(ids);
            btn.closest('.service-request-item').remove();
            recalcTotal();
            if (typeof removeFromCart === 'function') {
                removeFromCart(id);
            }
        });
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        var legal = form.querySelector('input[name="client_type"][value="legal"]').checked;
        var companyInput = document.getElementById('companyBin');
        var iinInput = document.getElementById('checkoutClientIin');
        if (legal && companyInput && !companyInput.value.trim()) {
            companyInput.setCustomValidity('Укажите БИН или официальное наименование компании');
            companyInput.reportValidity();
            return;
        }
        if (!legal && iinInput) {
            var iinDigits = (iinInput.value || '').replace(/\D/g, '');
            if (iinDigits.length !== 12) {
                iinInput.setCustomValidity('ИИН должен содержать 12 цифр');
                iinInput.reportValidity();
                return;
            }
            iinInput.value = iinDigits;
            iinInput.setCustomValidity('');
        }
        if (companyInput) companyInput.setCustomValidity('');

        if (!form.reportValidity() || !getIds().length) return;

        var submitBtn = form.querySelector('.service-request-submit');
        if (submitBtn) submitBtn.disabled = true;

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.success) {
                    if (typeof updateCartCounter === 'function') {
                        updateCartCounter(0);
                    }
                    var modalEl = document.getElementById('requestSentModal');
                    var numberEl = document.getElementById('requestSentNumber');
                    var statusBtn = document.getElementById('requestStatusBtn');
                    if (numberEl) numberEl.textContent = data.request_number || data.request_id;
                    if (statusBtn && data.status_url) statusBtn.href = data.status_url;
                    if (modalEl) {
                        new bootstrap.Modal(modalEl).show();
                    }
                    form.reset();
                    toggleClientTypeFields();
                } else if (messageBox) {
                    messageBox.hidden = false;
                    messageBox.className = 'service-request-message is-error';
                    messageBox.textContent = data.message || 'Ошибка отправки';
                }
            })
            .catch(function () {
                if (messageBox) {
                    messageBox.hidden = false;
                    messageBox.className = 'service-request-message is-error';
                    messageBox.textContent = 'Произошла ошибка при отправке заявки';
                }
            })
            .finally(function () {
                if (submitBtn) submitBtn.disabled = false;
            });
    });

    var closeBtn = document.getElementById('requestSentCloseBtn');
    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            window.location.href = '/services/';
        });
    }
})();
