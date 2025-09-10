// Функция для получения CSRF токена
function getCSRFToken() {
    let token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) {
        return token.value;
    }
    
    token = document.querySelector('meta[name="csrf-token"]');
    if (token) {
        return token.getAttribute('content');
    }
    
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Показ модального окна для неавторизованных пользователей
function showAuthModal() {
    const modalHtml = `
        <div class="modal fade" id="authRequiredModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <h5 class="modal-title text-primary">
                            <i class="fas fa-lock me-2"></i>Требуется авторизация
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center py-4">
                        <div class="mb-4">
                            <i class="fas fa-shopping-cart text-muted" style="font-size: 4rem;"></i>
                        </div>
                        <h6 class="mb-3">Получить услугу могут только авторизованные пользователи</h6>
                        <p class="text-muted mb-4">Войдите в свой аккаунт или создайте новый для добавления услуг в корзину</p>
                        <div class="d-grid gap-2">
                            <a href="/users/login/" class="btn btn-primary">
                                <i class="fas fa-sign-in-alt me-2"></i>Войти
                            </a>
                            <a href="/users/register/" class="btn btn-outline-primary">
                                <i class="fas fa-user-plus me-2"></i>Зарегистрироваться
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const existingModal = document.getElementById('authRequiredModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modal = new bootstrap.Modal(document.getElementById('authRequiredModal'));
    modal.show();
}

function showNotification(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas ${icon} me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 4000);
}

// Обновление счетчика корзины
function updateCartCounter(count) {
    const cartCounters = document.querySelectorAll('.cart-counter, .cart-count');
    cartCounters.forEach(counter => {
        counter.textContent = count;
        if (count > 0) {
            counter.style.display = 'flex';
        } else {
            counter.style.display = 'none';
        }
    });
}

// Добавление в корзину
function addToCart(serviceId, serviceName) {
    fetch(`/users/cart/add/${serviceId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            updateCartCounter(data.cart_count);
            
            const button = document.querySelector(`[onclick="addToCart(${serviceId}, '${serviceName}')"]`);
            if (button) {
                button.innerHTML = '<i class="fas fa-check me-2"></i>В корзине';
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
                button.disabled = true;
            }
        } else {
            if (data.auth_required) {
                showAuthModal();
            } else {
                showNotification(data.message, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Произошла ошибка при добавлении в корзину', 'error');
    });
}

function removeFromCart(serviceId, serviceName) {
    fetch(`/users/cart/remove/${serviceId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            updateCartCounter(data.cart_count);
            
            if (window.location.pathname.includes('/cart/')) {
                location.reload();
            }
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Произошла ошибка при удалении из корзины', 'error');
    });
}

function clearCart() {
    if (!confirm('Вы уверены, что хотите очистить корзину?')) {
        return;
    }
    
    fetch('/users/cart/clear/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            updateCartCounter(0);
            
            if (window.location.pathname.includes('/cart/')) {
                location.reload();
            }
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Произошла ошибка при очистке корзины', 'error');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('/users/cart/count/')
        .then(response => response.json())
        .then(data => {
            updateCartCounter(data.cart_count);
        })
        .catch(error => {
            console.error('Error loading cart count:', error);
        });
});