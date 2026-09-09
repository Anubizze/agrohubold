import re
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse

from .models import Project, Service, ServiceRequest

SESSION_GUEST_PROFILE = 'guest_client_profile'

VALID_REQUEST_TYPES = {'SERVICE', 'PROJECT', 'PROJECT_PROPOSAL', 'GENERAL'}
VALID_CATEGORIES = {'SERVICE', 'PROJECT', 'LABORATORY', 'EDUCATION', 'OTHER'}


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

    return queryset.prefetch_related('services', 'project').first()


def get_source_page(request):
    source = (request.POST.get('source_page') or '').strip()
    if source:
        return source[:500]
    referer = request.META.get('HTTP_REFERER', '')
    return referer[:500] if referer else ''


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


def hub_request_response(request_obj):
    return {
        'success': True,
        'message': 'Заявка отправлена! Мы свяжемся с вами в ближайшее время.',
        'request_id': request_obj.id,
        'request_number': request_obj.get_request_number(),
        'status_url': request_obj.get_status_url(),
    }


def send_service_request_email(service_request):
    request_number = service_request.get_request_number()
    status_url = service_request.get_status_url()
    context_label = service_request.get_context_label()

    type_labels = {
        'SERVICE': 'услуга',
        'PROJECT': 'проект',
        'PROJECT_PROPOSAL': 'предложение проекта',
        'GENERAL': 'общий запрос',
    }
    type_label = type_labels.get(service_request.request_type, 'заявка')

    subject = f'Заявка № {request_number} принята — Shakarim University'
    message = (
        f'Здравствуйте, {service_request.client_name}!\n\n'
        f'Мы получили вашу заявку № {request_number} ({type_label}).\n'
        f'Контекст: {context_label}\n\n'
        f'Проверить статус заявки:\n{status_url}\n\n'
        f'Чтобы сохранить историю заявок, зарегистрируйтесь на сайте с тем же email и ИИН.\n\n'
        f'С уважением,\nShakarim University'
    )

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@shakarim.kz')
    send_mail(subject, message, from_email, [service_request.client_email], fail_silently=True)


def create_hub_request(request, request_type, **fields):
    """Создание заявки единой системы с автоматическим контекстом."""
    request_type = (request_type or '').upper()
    if request_type not in VALID_REQUEST_TYPES:
        raise ValueError('Некорректный тип заявки')

    source_page = fields.pop('source_page', None) or get_source_page(request)
    attachment = fields.pop('attachment', None)

    hub_request = ServiceRequest(
        request_type=request_type,
        source_page=source_page,
        **fields,
    )
    if attachment:
        hub_request.attachment = attachment
    hub_request.save()
    return hub_request


def attach_service_context(hub_request, service):
    hub_request.object_type = 'SERVICE'
    hub_request.object_id = service.id
    hub_request.object_title = service.name
    hub_request.save(update_fields=['object_type', 'object_id', 'object_title'])


def attach_project_context(hub_request, project):
    hub_request.project = project
    hub_request.object_type = 'PROJECT'
    hub_request.object_id = project.id
    hub_request.object_title = project.title
    hub_request.save(update_fields=['project', 'object_type', 'object_id', 'object_title'])
