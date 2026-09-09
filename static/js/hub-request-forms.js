(function () {
    'use strict';

    function bindHubForm(formId, messageBoxId, modalId) {
        var form = document.getElementById(formId);
        if (!form) return;

        var messageBox = document.getElementById(messageBoxId);

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (!form.reportValidity()) return;

            var submitBtn = form.querySelector('.site-request__submit');
            if (submitBtn) submitBtn.disabled = true;

            var sourceField = form.querySelector('[name="source_page"]');
            if (sourceField) sourceField.value = window.location.pathname;

            fetch(form.getAttribute('action'), {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (!messageBox) return;
                    messageBox.hidden = false;
                    messageBox.textContent = data.message || (data.success ? 'Заявка отправлена' : 'Ошибка');
                    messageBox.className = 'site-request__message is-' + (data.success ? 'success' : 'error');
                    if (data.success) {
                        form.reset();
                        setTimeout(function () {
                            if (modalId) {
                                var modalEl = document.getElementById(modalId);
                                if (modalEl) {
                                    var instance = bootstrap.Modal.getInstance(modalEl);
                                    if (instance) instance.hide();
                                }
                            }
                            messageBox.hidden = true;
                        }, 2200);
                    }
                })
                .catch(function () {
                    if (messageBox) {
                        messageBox.hidden = false;
                        messageBox.className = 'site-request__message is-error';
                        messageBox.textContent = 'Произошла ошибка при отправке заявки';
                    }
                })
                .finally(function () {
                    if (submitBtn) submitBtn.disabled = false;
                });
        });
    }

    bindHubForm('projectCollaborationForm', 'projectCollaborationMessageBox', 'projectCollaborationModal');
    bindHubForm('projectProposalForm', 'projectProposalMessageBox', 'projectProposalModal');

    window.openProjectCollaborationModal = function (projectId, projectTitle) {
        var idField = document.getElementById('projectCollaborationId');
        var lead = document.getElementById('projectCollaborationLead');
        var source = document.getElementById('projectCollaborationSource');
        if (idField) idField.value = projectId || '';
        if (lead && projectTitle) {
            lead.textContent = (lead.getAttribute('data-default') || lead.textContent.split('—')[0].trim()) + ' — ' + projectTitle;
        }
        if (source) source.value = window.location.pathname;
    };

    var lead = document.getElementById('projectCollaborationLead');
    if (lead && !lead.getAttribute('data-default')) {
        lead.setAttribute('data-default', lead.textContent.trim());
    }
})();
