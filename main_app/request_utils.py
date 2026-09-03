import re
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse

from .models import ServiceRequest

SESSION_GUEST_PROFILE = 'guest_client_profile'


def normalize_iin(value):
    return ''.join(char for char in (value or '') if char.isdigit())


def parse_request_number(number):
    match = re.fullmatch(r'(\d{4})-(\d+)', (number or '').strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def find_service_request(number, token=None, email=None):
    parsed = parse_request_number(number)
    if not parsed:
        return None

    year, request_id = parsed
    queryset = ServiceRequest.objects.filter(id=request_id, created_at__year=year)

    if token:
        queryset = queryset.filter(tracking_token=token)
    if email:
        queryset = queryset.filter(client_email__iexact=email.strip())

    return queryset.prefetch_related('services').first()


def save_guest_client_profile(request, profile):
    request.session[SESSION_GUEST_PROFILE] = profile
    request.session.modified = True


def get_guest_client_profile(request):
    return request.session.get(SESSION_GUEST_PROFILE, {})


def link_service_requests_to_user(user):
    filters = Q()
    if user.email:
        filters |= Q(client_email__iexact=user.email)
    if user.iin:
        filters |= Q(client_iin=user.iin)

    if not filters:
        return 0

    return ServiceRequest.objects.filter(user__isnull=True).filter(filters).update(user=user)


def send_service_request_email(service_request):
    request_number = service_request.get_request_number()
    status_url = service_request.get_status_url()
    services_list = service_request.get_services_list()

    subject = f'Заявка № {request_number} принята — Shakarim University'
    message = (
        f'Здравствуйте, {service_request.client_name}!\n\n'
        f'Мы получили вашу заявку № {request_number}.\n'
        f'Услуги: {services_list}\n\n'
        f'Проверить статус заявки:\n{status_url}\n\n'
        f'Чтобы сохранить историю заявок, зарегистрируйтесь на сайте с тем же email и ИИН.\n\n'
        f'Специалист свяжется с вами для уточнения стоимости, сроков и условий выполнения.\n\n'
        f'С уважением,\nShakarim University'
    )

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@shakarim.kz')
    send_mail(subject, message, from_email, [service_request.client_email], fail_silently=True)
