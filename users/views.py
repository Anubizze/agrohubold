from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm
from .models import ServiceCart, ServicePayment
from main_app.models import Service, ServiceRequest
from main_app.request_utils import get_guest_client_profile, link_service_requests_to_user


SESSION_CART_KEY = 'cart_service_ids'


def _get_cart_ids(request):
    ids = request.session.get(SESSION_CART_KEY, [])
    return [int(i) for i in ids if str(i).isdigit()]


def _set_cart_ids(request, ids):
    request.session[SESSION_CART_KEY] = list(dict.fromkeys(int(i) for i in ids))
    request.session.modified = True


def _get_cart_services(request):
    ids = _get_cart_ids(request)
    if not ids:
        return Service.objects.none()
    services = Service.objects.filter(id__in=ids, is_active=True)
    order = {service_id: index for index, service_id in enumerate(ids)}
    return sorted(services, key=lambda service: order.get(service.id, 999))


def register_view(request):
    guest = get_guest_client_profile(request)
    initial = {}
    if guest:
        name_parts = (guest.get('client_name') or '').split()
        initial = {
            'email': guest.get('client_email', ''),
            'phone': guest.get('client_phone', ''),
            'iin': guest.get('client_iin', ''),
            'first_name': name_parts[0] if name_parts else '',
            'last_name': ' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
        }

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            linked = link_service_requests_to_user(user)
            messages.success(
                request,
                f'Аккаунт создан! Привязано заявок: {linked}.' if linked else 'Аккаунт создан! Теперь можете войти.'
            )
            return redirect('login')
    else:
        form = CustomUserCreationForm(initial=initial)
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            linked = link_service_requests_to_user(user)
            if linked:
                messages.success(request, f'Вход выполнен. В истории доступно заявок: {linked}.')
            return redirect('profile')
        messages.error(request, 'Неверные данные')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('/')


@login_required
def profile_view(request):
    cart_services = _get_cart_services(request)
    cart_total = sum(service.price for service in cart_services)

    payments = ServicePayment.objects.filter(user=request.user).prefetch_related('services').order_by('-created_at')
    service_requests = ServiceRequest.objects.filter(
        user=request.user
    ).prefetch_related('services').order_by('-created_at')

    total_orders = payments.count()
    approved_orders = payments.filter(status='approved').count()
    pending_orders = payments.filter(status='pending').count()

    context = {
        'cart_items': [{'service': service} for service in cart_services],
        'cart_total': cart_total,
        'cart_count': len(cart_services),
        'payments': payments,
        'service_requests': service_requests,
        'total_orders': total_orders,
        'approved_orders': approved_orders,
        'pending_orders': pending_orders,
    }

    return render(request, 'profile.html', context)


@require_POST
def add_to_cart(request, service_id):
    service = get_object_or_404(Service, id=service_id, is_active=True)
    ids = _get_cart_ids(request)

    if service_id in ids:
        return JsonResponse({
            'success': False,
            'message': 'Услуга уже в заявке',
            'cart_count': len(ids),
            'service_name': service.name,
        })

    ids.append(service_id)
    _set_cart_ids(request, ids)

    return JsonResponse({
        'success': True,
        'message': f'Услуга "{service.name}" добавлена в заявку',
        'cart_count': len(ids),
        'service_name': service.name,
    })


@require_POST
def remove_from_cart(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    ids = _get_cart_ids(request)

    if service_id not in ids:
        return JsonResponse({
            'success': False,
            'message': 'Услуга не найдена в заявке',
            'cart_count': len(ids),
        })

    ids = [item_id for item_id in ids if item_id != service_id]
    _set_cart_ids(request, ids)

    return JsonResponse({
        'success': True,
        'message': f'Услуга "{service.name}" удалена из заявки',
        'cart_count': len(ids),
    })


@require_POST
def clear_cart(request):
    ids = _get_cart_ids(request)
    deleted_count = len(ids)
    _set_cart_ids(request, [])

    return JsonResponse({
        'success': True,
        'message': f'Заявка очищена ({deleted_count} услуг удалено)',
        'cart_count': 0,
    })


def cart_view(request):
    services = _get_cart_services(request)
    total_amount = sum(service.price for service in services)

    context = {
        'cart_items': [{'service': service} for service in services],
        'total_amount': total_amount,
        'cart_count': len(services),
    }

    return render(request, 'cart.html', context)


def get_cart_count(request):
    return JsonResponse({'cart_count': len(_get_cart_ids(request))})


def checkout_view(request):
    services = list(_get_cart_services(request))

    if not services:
        messages.warning(request, 'В заявке пока нет услуг')
        return redirect('services_list')

    total_amount = sum(service.price for service in services)
    guest = get_guest_client_profile(request)

    if request.user.is_authenticated:
        user_name = request.user.get_full_name()
        user_phone = getattr(request.user, 'phone', '')
        user_email = request.user.email
        user_iin = getattr(request.user, 'iin', '')
    else:
        user_name = guest.get('client_name', '')
        user_phone = guest.get('client_phone', '')
        user_email = guest.get('client_email', '')
        user_iin = guest.get('client_iin', '')

    context = {
        'cart_services': services,
        'total_amount': total_amount,
        'cart_count': len(services),
        'user_phone': user_phone,
        'user_email': user_email,
        'user_name': user_name,
        'user_iin': user_iin,
        'guest_client_type': guest.get('client_type', 'individual'),
        'guest_company_bin': guest.get('company_bin', ''),
    }

    return render(request, 'checkout.html', context)


@login_required
@require_POST
def process_payment(request):
    cart_items = ServiceCart.objects.filter(user=request.user).select_related('service')

    if not cart_items.exists():
        return JsonResponse({
            'success': False,
            'message': 'Корзина пуста'
        })

    if 'receipt_file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'message': 'Необходимо загрузить чек'
        })

    receipt_file = request.FILES['receipt_file']

    if receipt_file.size > 10 * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'message': 'Размер файла не должен превышать 10MB'
        })

    total_amount = sum(item.service.price for item in cart_items)

    payment = ServicePayment.objects.create(
        user=request.user,
        total_amount=total_amount,
        receipt_file=receipt_file,
        status='pending'
    )

    services = [item.service for item in cart_items]
    payment.services.set(services)

    try:
        payment.generate_act_file()
        payment.save()
    except Exception as e:
        print(f"Ошибка генерации акта: {e}")

    cart_items.delete()

    return JsonResponse({
        'success': True,
        'message': 'Чек успешно загружен! Ваш заказ отправлен на проверку.',
        'payment_id': payment.id
    })


@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(ServicePayment, id=payment_id, user=request.user)

    context = {
        'payment': payment,
        'services': payment.services.all(),
    }

    return render(request, 'payment_success.html', context)
