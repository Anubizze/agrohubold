from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm
from .models import ServiceCart, ServicePayment
from main_app.models import Service

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Аккаунт создан для {user.get_full_name()}! Теперь можете войти.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('profile')
        messages.error(request, 'Неверные данные')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('/')

@login_required
def profile_view(request):
    cart_items = ServiceCart.objects.filter(user=request.user).select_related('service')
    cart_total = sum(item.service.price for item in cart_items)
    
    payments = ServicePayment.objects.filter(user=request.user).prefetch_related('services').order_by('-created_at')
    
    total_orders = payments.count()
    approved_orders = payments.filter(status='approved').count()
    pending_orders = payments.filter(status='pending').count()
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_items.count(),
        'payments': payments,
        'total_orders': total_orders,
        'approved_orders': approved_orders,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'profile.html', context)

@require_POST
def add_to_cart(request, service_id):
    """Добавление услуги в корзину"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Для добавления в корзину необходимо войти в аккаунт',
            'auth_required': True
        })
    
    service = get_object_or_404(Service, id=service_id, is_active=True)
    
    # Проверяем, нет ли уже в корзине
    cart_item, created = ServiceCart.objects.get_or_create(
        user=request.user,
        service=service
    )
    
    if created:
        return JsonResponse({
            'success': True,
            'message': f'Услуга "{service.name}" добавлена в корзину',
            'cart_count': ServiceCart.objects.filter(user=request.user).count()
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Услуга уже в корзине'
        })

@login_required
@require_POST
def remove_from_cart(request, service_id):
    """Удаление услуги из корзины"""
    service = get_object_or_404(Service, id=service_id)
    
    try:
        cart_item = ServiceCart.objects.get(user=request.user, service=service)
        cart_item.delete()
        return JsonResponse({
            'success': True,
            'message': f'Услуга "{service.name}" удалена из корзины',
            'cart_count': ServiceCart.objects.filter(user=request.user).count()
        })
    except ServiceCart.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Услуга не найдена в корзине'
        })

@login_required
@require_POST
def clear_cart(request):
    """Очистка корзины"""
    deleted_count = ServiceCart.objects.filter(user=request.user).delete()[0]
    
    return JsonResponse({
        'success': True,
        'message': f'Корзина очищена ({deleted_count} услуг удалено)',
        'cart_count': 0
    })

@login_required
def cart_view(request):
    """Просмотр корзины"""
    cart_items = ServiceCart.objects.filter(user=request.user).select_related('service')
    total_amount = sum(item.service.price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'cart_count': cart_items.count()
    }
    
    return render(request, 'cart.html', context)

def get_cart_count(request):
    """Получение количества товаров в корзине для AJAX"""
    if request.user.is_authenticated:
        count = ServiceCart.objects.filter(user=request.user).count()
    else:
        count = 0
    
    return JsonResponse({'cart_count': count})


@login_required
def checkout_view(request):
    """Страница оформления заказа"""
    cart_items = ServiceCart.objects.filter(user=request.user).select_related('service')
    
    if not cart_items.exists():
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart')
    
    total_amount = sum(item.service.price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'cart_count': cart_items.count(),
        'user_phone': request.user.phone,
        'user_email': request.user.email,
    }
    
    return render(request, 'checkout.html', context)

@login_required
@require_POST
def process_payment(request):
    """Обработка загруженного чека"""
    cart_items = ServiceCart.objects.filter(user=request.user).select_related('service')
    
    if not cart_items.exists():
        return JsonResponse({
            'success': False,
            'message': 'Корзина пуста'
        })
    
    # Проверяем наличие файла
    if 'receipt_file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'message': 'Необходимо загрузить чек'
        })
    
    receipt_file = request.FILES['receipt_file']
    
    # Проверяем размер файла (максимум 10MB)
    if receipt_file.size > 10 * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'message': 'Размер файла не должен превышать 10MB'
        })
    
    # Создаем платеж
    total_amount = sum(item.service.price for item in cart_items)
    
    payment = ServicePayment.objects.create(
        user=request.user,
        total_amount=total_amount,
        receipt_file=receipt_file,
        status='pending'
    )
    
    # Добавляем услуги к платежу
    services = [item.service for item in cart_items]
    payment.services.set(services)
    
    # Генерируем акт автоматически
    try:
        payment.generate_act_file()
        payment.save()
    except Exception as e:
        # Если не удалось сгенерировать акт, логируем ошибку но не прерываем процесс
        print(f"Ошибка генерации акта: {e}")
    
    # Очищаем корзину после успешного создания платежа
    cart_items.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Чек успешно загружен! Ваш заказ отправлен на проверку.',
        'payment_id': payment.id
    })

@login_required
def payment_success(request, payment_id):
    """Страница успешной оплаты"""
    payment = get_object_or_404(ServicePayment, id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
        'services': payment.services.all(),
    }
    
    return render(request, 'payment_success.html', context)