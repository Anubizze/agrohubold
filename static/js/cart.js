function getCSRFToken() {
    var token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) return token.value;

    token = document.querySelector('meta[name="csrf-token"]');
    if (token) return token.getAttribute('content');

    var name = 'csrftoken';
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type) {
    type = type || 'success';
    var alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    var icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';

    var notification = document.createElement('div');
    notification.className = 'alert ' + alertClass + ' alert-dismissible fade show position-fixed';
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = '<i class="fas ' + icon + ' me-2"></i>' + message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    document.body.appendChild(notification);

    setTimeout(function () {
        if (notification.parentNode) notification.remove();
    }, 4000);
}

function updateCartCounter(count) {
    document.querySelectorAll('.cart-counter, .cart-count').forEach(function (counter) {
        counter.textContent = count;
        counter.style.display = count > 0 ? 'flex' : 'none';
    });
}

function showCartAddedModal(serviceName) {
    var nameEl = document.getElementById('cartAddedServiceName');
    if (nameEl) nameEl.textContent = serviceName;
    var modalEl = document.getElementById('cartAddedModal');
    if (modalEl) new bootstrap.Modal(modalEl).show();
}

function addToCart(serviceId, serviceName) {
    fetch('/users/cart/add/' + serviceId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                updateCartCounter(data.cart_count);
                showCartAddedModal(data.service_name || serviceName);
            } else if (data.message === 'Услуга уже в заявке') {
                updateCartCounter(data.cart_count);
                showNotification(data.message, 'error');
            } else {
                showNotification(data.message || 'Ошибка', 'error');
            }
        })
        .catch(function () {
            showNotification('Произошла ошибка при добавлении в заявку', 'error');
        });
}

function removeFromCart(serviceId) {
    fetch('/users/cart/remove/' + serviceId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                updateCartCounter(data.cart_count);
                if (window.location.pathname.indexOf('/cart/') !== -1) {
                    location.reload();
                }
            } else {
                showNotification(data.message, 'error');
            }
        });
}

function clearCart() {
    if (!confirm('Очистить заявку?')) return;

    fetch('/users/cart/clear/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.success) {
                updateCartCounter(0);
                if (window.location.pathname.indexOf('/cart/') !== -1 ||
                    window.location.pathname.indexOf('/checkout/') !== -1) {
                    location.reload();
                }
            }
        });
}

document.addEventListener('DOMContentLoaded', function () {
    fetch('/users/cart/count/')
        .then(function (response) { return response.json(); })
        .then(function (data) { updateCartCounter(data.cart_count); })
        .catch(function () {});
});
