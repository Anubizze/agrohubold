import os
import json
from django.db.models import Q, Prefetch
from .models import *
from .contact_utils import (
    entity_to_contact_column,
    get_service_catalog_contact_columns,
    has_contact_content,
    innovation_office_contact_column,
)
from .request_utils import (
    attach_project_context,
    attach_service_context,
    create_hub_request,
    find_service_request,
    get_guest_client_profile,
    get_source_page,
    hub_request_response,
    link_service_requests_to_user,
    normalize_iin,
    save_guest_client_profile,
    send_service_request_email,
    VALID_CATEGORIES,
)
from django.conf import settings
from django.utils import translation
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404

def reload_translations_view(request):
    if request.user.is_superuser:
        os.system(f'cd "{settings.BASE_DIR}" && python manage.py compilemessages')
        wsgi_path = settings.BASE_DIR / 'agrohub' / 'wsgi.py'
        if wsgi_path.exists():
            os.utime(wsgi_path, None)
        return HttpResponse("Переводы обновлены")
    return HttpResponse("Нет прав доступа", status=403)

def index(request):
    locale = translation.get_language()
    latest_news = News.objects.filter(is_published=True, is_expert_news=False, is_guide=False).order_by('-created_at')[:3]
    home_page = HomePageSettings.get_solo()
    home_slides = home_page.slides.filter(is_active=True).order_by('order', 'id')

    context = {
        'current_language': locale,
        'latest_news': latest_news,
        'home_page': home_page,
        'home_slides': home_slides,
    }
    return render(request, 'index.html', context)


def things_list(request):
    """List all things with translations"""
    locale = translation.get_language()
    things = Thing.objects.all()
    
    context = {
        'things': things,
        'current_language': locale,
    }
    return render(request, 'things.html', context)


def about(request):
    locale = translation.get_language()
    about_page = AboutPageSettings.get_solo()
    context = {
        'current_language': locale,
        'about_page': about_page,
    }
    return render(request, 'about.html', context)

def team(request):
    locale = translation.get_language()
    departments = (
        TeamDepartment.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                'members',
                queryset=TeamMember.objects.filter(is_active=True).order_by('order', 'name'),
            )
        )
        .order_by('order', 'name')
    )
    context = {
        'current_language': locale,
        'departments': departments,
        'team_page': TeamPageSettings.get_solo(),
    }
    return render(request, 'team.html', context)

def lab(request):
    locale = translation.get_language()
    lab_page = LabPageSettings.get_solo()
    context = {
        'current_language': locale,
        'lab_page': lab_page,
        'lab_service_cards': lab_page.service_cards.filter(is_active=True).order_by('order', 'id'),
    }
    return render(request, 'labs/lab.html', context)

def agrotehnopark(request):
    """Агротехнопарк объединён с Shakarim Lab."""
    return redirect('lab')

def engeneering_center(request):
    locale = translation.get_language()
    eng_page = EngineeringPageSettings.get_solo()
    context = {
        'current_language': locale,
        'eng_page': eng_page,
        'eng_service_cards': eng_page.service_cards.filter(is_active=True).order_by('order', 'id'),
    }
    return render(request, 'labs/engeneering_center.html', context)

def change_language(request, language_code):
    """Change the current language"""
    if language_code in [lang[0] for lang in settings.LANGUAGES]:
        request.session[settings.LANGUAGE_SESSION_KEY] = language_code
        translation.activate(language_code)

    # Redirect back to the previous page
    previous_page = request.META.get('HTTP_REFERER')
    if previous_page:
        return redirect(previous_page)
    else:
        return redirect('/')


def news_list(request):
    news = News.objects.filter(is_published=True, is_expert_news=False, is_guide=False)
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        news = news.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Фильтр по категории
    category_filter = request.GET.get('category', '')
    if category_filter and category_filter != 'all':
        news = news.filter(category__slug=category_filter)
    
    # Фильтр по периоду
    period_filter = request.GET.get('period', '3months')
    if period_filter == '1month':
        date_from = datetime.now() - timedelta(days=30)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '3months':
        date_from = datetime.now() - timedelta(days=90)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '6months':
        date_from = datetime.now() - timedelta(days=180)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '1year':
        date_from = datetime.now() - timedelta(days=365)
        news = news.filter(created_at__gte=date_from)
    
    # Сортировка
    sort_filter = request.GET.get('sort', 'newest')
    if sort_filter == 'newest':
        news = news.order_by('-created_at')
    elif sort_filter == 'oldest':
        news = news.order_by('created_at')
    elif sort_filter == 'title':
        news = news.order_by('title')
    
    # Пагинация
    paginator = Paginator(news, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Категории для фильтра
    categories = NewsCategory.objects.filter(type='news')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'period_filter': period_filter,
        'sort_filter': sort_filter,
        'news_page': NewsPageSettings.get_solo(),
    }
    
    return render(request, 'news.html', context)


def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk, is_published=True)
    related_news = News.objects.filter(
        category=news.category, 
        is_published=True,
        is_expert_news=False,
        is_guide=False
    ).exclude(pk=pk)[:3]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    
    return render(request, 'news_detail.html', context)


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', '')
    
    if not email:
        return JsonResponse({
            'success': False, 
            'message': _('Email адрес обязателен')
        })
    
    newsletter, created = Newsletter.objects.get_or_create(email=email)
    
    if created:
        return JsonResponse({
            'success': True,
            'message': _('Вы успешно подписались на рассылку!')
        })
    else:
        return JsonResponse({
            'success': False,
            'message': _('Этот email уже подписан на рассылку')
        })


def services_list(request):
    """Страница списка услуг"""
    # Фильтры
    provider_filter = request.GET.get('provider', '')
    category_filter = request.GET.get('category', '')
    
    # Получаем все активные услуги
    services = Service.objects.filter(is_active=True).select_related(
        'category', 'category__provider', 'contact_member',
    )
    
    # Применяем фильтры
    if provider_filter:
        services = services.filter(category__provider__slug=provider_filter)
    
    if category_filter:
        services = services.filter(category__slug=category_filter)
        try:
            selected_category = ServiceCategory.objects.get(slug=category_filter)
            services = services.filter(category__provider=selected_category.provider)
        except ServiceCategory.DoesNotExist:
            pass
    
    # Пагинация
    paginator = Paginator(services, 50)  # все услуги направления на одной странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Данные для фильтров
    providers = ServiceProvider.objects.filter(is_active=True)
    
    # Категории зависят от выбранного провайдера
    categories = ServiceCategory.objects.filter(is_active=True)
    if provider_filter and provider_filter != 'all':
        categories = categories.filter(provider__slug=provider_filter)
    categories = categories.order_by('order', 'name')
    
    # Текущая активная акция (если есть)
    current_promotion = None

    is_catalog_mode = bool(category_filter or provider_filter or request.GET.get('dir'))
    contact_columns = []
    if is_catalog_mode:
        contact_columns = get_service_catalog_contact_columns(services, provider_filter, category_filter)
    
    context = {
        'page_obj': page_obj,
        'providers': providers,
        'categories': categories,
        'provider_filter': provider_filter,
        'category_filter': category_filter,
        'current_promotion': current_promotion,
        'services_page': ServicesPageSettings.get_solo(),
        'is_catalog_mode': is_catalog_mode,
        'contact_columns': contact_columns,
    }
    
    return render(request, 'services.html', context)


@require_POST
def cart_service_request(request):
    """Создание заявки на консультацию для нескольких услуг из корзины"""
    try:
        service_ids_json = request.POST.get('service_ids')
        client_name = request.POST.get('client_name', '').strip()
        client_email = request.POST.get('client_email', '').strip()
        client_phone = request.POST.get('client_phone', '').strip()
        message = request.POST.get('message', '').strip()
        client_type = request.POST.get('client_type', 'individual').strip()
        company_bin = request.POST.get('company_bin', '').strip()
        client_iin = normalize_iin(request.POST.get('client_iin', ''))
        consent = request.POST.get('consent')

        if not all([service_ids_json, client_name, client_email, client_phone, consent]):
            return JsonResponse({
                'success': False,
                'message': 'Заполните все обязательные поля'
            })

        if client_type == 'legal' and not company_bin:
            return JsonResponse({
                'success': False,
                'message': 'Укажите БИН или официальное наименование компании'
            })

        if client_type == 'individual' and len(client_iin) != 12:
            return JsonResponse({
                'success': False,
                'message': 'Укажите корректный ИИН (12 цифр)'
            })

        try:
            service_ids = json.loads(service_ids_json)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Ошибка в данных заявки'
            })

        services = Service.objects.filter(id__in=service_ids, is_active=True)

        if not services.exists():
            return JsonResponse({
                'success': False,
                'message': 'Выбранные услуги не найдены'
            })

        message_parts = []
        if message:
            message_parts.append(message)

        attachment = request.FILES.get('attachment')
        if attachment:
            message_parts.append(f'[Файл: {attachment.name}]')

        service_request = create_hub_request(
            request,
            'SERVICE',
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            client_type=client_type,
            company_bin=company_bin if client_type == 'legal' else '',
            client_iin=client_iin if client_type == 'individual' else '',
            message='\n\n'.join(message_parts).strip(),
            user=request.user if request.user.is_authenticated else None,
            attachment=attachment,
        )

        service_request.services.set(services)
        if services.count() == 1:
            attach_service_context(service_request, services.first())
        else:
            service_request.object_type = 'SERVICE'
            service_request.object_title = ', '.join(s.name for s in services)
            service_request.save(update_fields=['object_type', 'object_title'])
        service_request.calculate_total()

        if not request.user.is_authenticated:
            save_guest_client_profile(request, {
                'client_name': client_name,
                'client_email': client_email,
                'client_phone': client_phone,
                'client_iin': client_iin,
                'client_type': client_type,
                'company_bin': company_bin if client_type == 'legal' else '',
            })
        elif request.user.is_authenticated and client_type == 'individual' and client_iin and not request.user.iin:
            request.user.iin = client_iin
            request.user.save(update_fields=['iin'])

        if request.user.is_authenticated:
            link_service_requests_to_user(request.user)

        if 'cart_service_ids' in request.session:
            request.session['cart_service_ids'] = []
            request.session.modified = True

        send_service_request_email(service_request)

        services_names = [service.name for service in services]
        request_number = service_request.get_request_number()

        return JsonResponse({
            'success': True,
            'message': 'Заявка отправлена! Мы свяжемся с вами в ближайшее время.',
            'request_id': service_request.id,
            'request_number': request_number,
            'status_url': service_request.get_status_url(),
            'services_summary': ', '.join(services_names),
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Произошла ошибка: {str(e)}'
        })


def service_request_status(request):
    service_request_obj = None
    error_message = ''
    lookup_number = request.GET.get('number', '').strip()
    lookup_token = request.GET.get('token', '').strip()

    if request.method == 'POST':
        lookup_number = request.POST.get('number', '').strip()
        lookup_email = request.POST.get('email', '').strip()
        service_request_obj = find_service_request(lookup_number, email=lookup_email)
        if not service_request_obj:
            error_message = _('request_status_not_found')
    elif lookup_number and lookup_token:
        service_request_obj = find_service_request(lookup_number, token=lookup_token)
        if not service_request_obj:
            error_message = _('request_status_not_found')

    context = {
        'service_request': service_request_obj,
        'error_message': error_message,
        'lookup_number': lookup_number,
    }
    return render(request, 'request_status.html', context)


@require_POST
def general_service_request(request):
    """Общая форма «Не нашли то, что искали?» — тип GENERAL."""
    try:
        client_name = request.POST.get('client_name', '').strip()
        client_email = request.POST.get('client_email', '').strip()
        client_phone = request.POST.get('client_phone', '').strip()
        category = request.POST.get('category', '').strip().upper()
        message = request.POST.get('message', '').strip()
        consent = request.POST.get('consent')
        object_type = request.POST.get('object_type', '').strip().upper()
        object_id = request.POST.get('object_id', '').strip()
        object_title = request.POST.get('object_title', '').strip()

        if not all([client_name, client_email, client_phone, message, consent]):
            return JsonResponse({
                'success': False,
                'message': 'Заполните все обязательные поля'
            })

        if category not in VALID_CATEGORIES:
            return JsonResponse({
                'success': False,
                'message': 'Выберите, что вас интересует'
            })

        attachment = request.FILES.get('attachment')

        hub_request = create_hub_request(
            request,
            'GENERAL',
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            category=category,
            message=message,
            object_type=object_type if object_type in {'SERVICE', 'PROJECT', 'LABORATORY'} else '',
            object_id=int(object_id) if object_id.isdigit() else None,
            object_title=object_title,
            user=request.user if request.user.is_authenticated else None,
            attachment=attachment,
        )

        send_service_request_email(hub_request)
        return JsonResponse(hub_request_response(hub_request))
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Произошла ошибка: {str(e)}'
        })


@require_POST
def project_collaboration_request(request):
    """Заявка на сотрудничество по конкретному проекту — тип PROJECT."""
    try:
        project_id = request.POST.get('project_id', '').strip()
        client_name = request.POST.get('client_name', '').strip()
        client_email = request.POST.get('client_email', '').strip()
        client_phone = request.POST.get('client_phone', '').strip()
        message = request.POST.get('message', '').strip()
        consent = request.POST.get('consent')

        if not all([project_id, client_name, client_email, client_phone, consent]):
            return JsonResponse({
                'success': False,
                'message': 'Заполните все обязательные поля'
            })

        project = get_object_or_404(Project, id=project_id, is_published=True)
        attachment = request.FILES.get('attachment')

        hub_request = create_hub_request(
            request,
            'PROJECT',
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            message=message,
            user=request.user if request.user.is_authenticated else None,
            attachment=attachment,
        )
        attach_project_context(hub_request, project)

        send_service_request_email(hub_request)
        return JsonResponse({
            **hub_request_response(hub_request),
            'message': f'Заявка по проекту «{project.title}» отправлена!',
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Произошла ошибка: {str(e)}'
        })


@require_POST
def project_proposal_request(request):
    """Предложение собственного проекта — тип PROJECT_PROPOSAL."""
    try:
        proposal_title = request.POST.get('proposal_title', '').strip()
        client_name = request.POST.get('client_name', '').strip()
        client_email = request.POST.get('client_email', '').strip()
        client_phone = request.POST.get('client_phone', '').strip()
        message = request.POST.get('message', '').strip()
        consent = request.POST.get('consent')

        if not all([proposal_title, client_name, client_email, client_phone, message, consent]):
            return JsonResponse({
                'success': False,
                'message': 'Заполните все обязательные поля'
            })

        attachment = request.FILES.get('attachment')

        hub_request = create_hub_request(
            request,
            'PROJECT_PROPOSAL',
            proposal_title=proposal_title,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            message=message,
            user=request.user if request.user.is_authenticated else None,
            attachment=attachment,
        )

        send_service_request_email(hub_request)
        return JsonResponse(hub_request_response(hub_request))
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Произошла ошибка: {str(e)}'
        })


@require_POST  
def service_request(request):
    """Консультация по одной услуге — тип SERVICE."""
    try:
        service_id = request.POST.get('service_id')
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        message = request.POST.get('message', '')
        consent = request.POST.get('consent')
        
        if not all([service_id, client_name, client_email, client_phone]):
            return JsonResponse({
                'success': False,
                'message': 'Заполните все обязательные поля'
            })

        if not consent:
            return JsonResponse({
                'success': False,
                'message': 'Подтвердите согласие на обработку данных'
            })
        
        service = get_object_or_404(Service, id=service_id, is_active=True)
        attachment = request.FILES.get('attachment')
        
        hub_request = create_hub_request(
            request,
            'SERVICE',
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            message=message,
            user=request.user if request.user.is_authenticated else None,
            attachment=attachment,
        )
        
        hub_request.services.add(service)
        attach_service_context(hub_request, service)
        hub_request.calculate_total()
        send_service_request_email(hub_request)
        
        return JsonResponse({
            **hub_request_response(hub_request),
            'message': f'Заявка на консультацию по услуге «{service.name}» создана!',
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Произошла ошибка: {str(e)}'
        })
        
          
def service_detail(request, slug):
    """Детальная страница услуги"""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    related_services = Service.objects.filter(
        category=service.category,
        is_active=True
    ).exclude(slug=slug)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    
    return render(request, 'service_detail.html', context)

# def courses(request):
#     locale = translation.get_language()
    
#     context = {
#         'current_language': locale,
#     }
#     return render(request, 'courses.html', context)

def course(request):
    locale = translation.get_language()
    
    context = {
        'current_language': locale,
    }
    return render(request, 'course.html', context)

def courses_list(request):
    """Страница списка курсов с фильтрацией"""
    # Фильтры
    category_filter = request.GET.get('category', '')
    filter_type = request.GET.get('filter', 'all')  # all, popular, discount
    
    # Получаем все активные курсы
    courses = Course.objects.filter(is_active=True).select_related('category')
    
    # Применяем фильтры по типу
    if filter_type == 'popular':
        courses = courses.filter(is_popular=True)
    elif filter_type == 'discount':
        courses = courses.filter(has_discount=True)
    
    # Фильтр по категории
    if category_filter:
        courses = courses.filter(category__slug=category_filter)
    
    # Сортировка
    courses = courses.order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(courses, 9)  # 9 курсов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Данные для фильтров
    categories = CourseCategory.objects.filter(is_active=True).order_by('order', 'name')
    
    locale = translation.get_language()
    office = InnovationOfficeSettings.get_solo()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'filter_type': filter_type,
        'current_language': locale,
        'courses_page': CoursesPageSettings.get_solo(),
        'contact_columns': [innovation_office_contact_column()],
        'contact_lead': office.lead,
    }
    
    return render(request, 'courses.html', context)


def course_detail(request, slug):
    """Детальная страница курса"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Получаем модули с темами
    modules = course.modules.filter().order_by('order').prefetch_related('topics')
    
    # Получаем преподавателей
    instructors = course.instructors.all()
    
    # Получаем одобренные отзывы
    reviews = course.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Похожие курсы
    related_courses = Course.objects.filter(
        category=course.category,
        is_active=True
    ).exclude(slug=slug)[:3]
    
    contact_column = course.get_contact_column()
    context = {
        'course': course,
        'modules': modules,
        'instructors': instructors,
        'reviews': reviews,
        'related_courses': related_courses,
        'contact_columns': [contact_column] if has_contact_content(contact_column) else [],
    }
    
    return render(request, 'course.html', context)


def course_application(request):
    """Обработка заявок на курс"""
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course_id')
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            # Валидация
            if not all([course_id, full_name, phone, email]):
                return JsonResponse({
                    'success': False,
                    'message': 'Заполните все обязательные поля'
                })
            
            # Получаем курс
            try:
                course = Course.objects.get(id=course_id, is_active=True)
            except Course.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Курс не найден'
                })
            
            # Создаем заявку
            application = CourseApplication.objects.create(
                course=course,
                full_name=full_name,
                phone=phone,
                email=email,
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Заявка на курс "{course.title}" успешно отправлена!',
                'application_id': application.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Произошла ошибка: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Метод не поддерживается'
    })



def knowledge_list(request):
    locale = translation.get_language()
    
    context = {
        'current_language': locale,
    }
    return render(request, 'knowledge_list.html', context)
  
def projects_catalog(request):
    """Каталог проектов и объектов интеллектуальной собственности."""
    catalog_type = request.GET.get('type', 'projects')
    is_ip = catalog_type == 'ip'
    settings = ProjectsCatalogSettings.get_solo()

    directions = ProjectDirection.objects.filter(is_active=True).order_by('order', 'name')
    statuses = ProjectStatus.objects.filter(is_active=True).order_by('order')
    total_projects = Project.objects.filter(is_published=True).count()

    context = {
        'is_ip': is_ip,
        'catalog_settings': settings,
        'directions': directions,
        'statuses': statuses,
        'total_projects': total_projects,
        'direction_filter': None,
        'status_filter': None,
        'patent_type_filter': None,
        'search_query': '',
        'projects': [],
        'patents': [],
        'patent_types': [],
        'page_obj': None,
        'total_patents': 0,
    }

    if is_ip:
        patents = Patent.objects.filter(is_published=True).select_related('patent_type')
        patent_type_slug = request.GET.get('ptype')
        search_query = request.GET.get('search', '').strip()

        if patent_type_slug:
            patents = patents.filter(patent_type__slug=patent_type_slug)
        if search_query:
            patents = patents.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(registration_number__icontains=search_query)
            )

        patents = patents.order_by('order', '-registration_date', '-created_at')
        paginator = Paginator(patents, 8)
        page_obj = paginator.get_page(request.GET.get('page'))

        context.update({
            'patents': page_obj.object_list,
            'page_obj': page_obj,
            'patent_types': PatentType.objects.filter(is_active=True).order_by('order', 'name'),
            'patent_type_filter': patent_type_slug,
            'search_query': search_query,
            'total_patents': paginator.count,
        })
    else:
        projects = Project.objects.filter(is_published=True).select_related('direction', 'status')
        direction_slug = request.GET.get('direction')
        status_slug = request.GET.get('status')
        search_query = request.GET.get('search', '').strip()

        if direction_slug:
            projects = projects.filter(direction__slug=direction_slug)
        if status_slug:
            projects = projects.filter(status__slug=status_slug)
        if search_query:
            projects = projects.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        projects = projects.order_by('-is_featured', '-created_at')
        paginator = Paginator(projects, 6)
        page_obj = paginator.get_page(request.GET.get('page'))

        context.update({
            'projects': page_obj.object_list,
            'page_obj': page_obj,
            'direction_filter': direction_slug,
            'status_filter': status_slug,
            'search_query': search_query,
            'total_projects': paginator.count,
        })

    return render(request, 'projects/catalog.html', context)

def project_detail(request, slug):
    """Детальная страница проекта"""
    
    # Получаем проект со всеми связанными данными
    project = get_object_or_404(
        Project.objects.select_related('direction', 'status')
                      .prefetch_related(
                          'images',
                          'team_members',
                          'info_panels',
                          'content_blocks',
                          'result_metrics',
                          'result_tables__rows',
                          'videos',
                      ),
        slug=slug,
        is_published=True
    )
    
    # Получаем похожие проекты (того же направления, исключая текущий)
    similar_projects = Project.objects.filter(
        direction=project.direction,
        is_published=True
    ).exclude(id=project.id).order_by('-is_featured', '-created_at')[:3]
    
    # Получаем все изображения проекта
    project_images = project.images.all().order_by('order')
    
    # Получаем команду проекта
    team_members = project.team_members.all()
    info_panels = project.info_panels.filter(is_active=True).order_by('order', 'id')
    inline_panels = [panel for panel in info_panels if panel.display_mode == ProjectInfoPanel.DISPLAY_INLINE]
    modal_panels = [panel for panel in info_panels if panel.display_mode == ProjectInfoPanel.DISPLAY_MODAL]
    content_blocks = project.content_blocks.filter(is_active=True).order_by('order', 'id')
    about_blocks = [b for b in content_blocks if b.section == ProjectContentBlock.SECTION_ABOUT]
    result_blocks = [b for b in content_blocks if b.section == ProjectContentBlock.SECTION_RESULTS]
    result_metrics = project.result_metrics.filter(is_active=True).order_by('order', 'id')
    result_tables = list(project.result_tables.filter(is_active=True).order_by('order', 'id'))
    project_videos = project.videos.filter(is_active=True).order_by('order', 'id')
    technologies = project.get_technologies_list()
    
    contact_column = project.get_contact_column()
    if not has_contact_content(contact_column) and team_members.exists():
        lead = team_members.first()
        contact_column = entity_to_contact_column(
            title=project.title,
            org=project.contact_org or 'НАО «Shakarim University»',
            division=project.contact_division or project.direction.name,
            person=lead.name,
            email=project.contact_email,
            phone=project.contact_phone,
            address=project.contact_address,
        )

    context = {
        'project': project,
        'similar_projects': similar_projects,
        'project_images': project_images,
        'team_members': team_members,
        'inline_panels': inline_panels,
        'modal_panels': modal_panels,
        'content_blocks': about_blocks,
        'result_blocks': result_blocks,
        'result_metrics': result_metrics,
        'result_tables': result_tables,
        'tables_use_accordion': len(result_tables) > 3,
        'project_videos': project_videos,
        'technologies': technologies,
        'project_contact_columns': [contact_column] if has_contact_content(contact_column) else [],
    }
    
    return render(request, 'projects/detail.html', context)

def expert_blog_list(request):
    news = News.objects.filter(is_published=True, is_expert_news=True)
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        news = news.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Фильтр по категории
    category_filter = request.GET.get('category', '')
    if category_filter and category_filter != 'all':
        news = news.filter(category__slug=category_filter)
    
    # Фильтр по периоду
    period_filter = request.GET.get('period', '3months')
    if period_filter == '1month':
        date_from = datetime.now() - timedelta(days=30)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '3months':
        date_from = datetime.now() - timedelta(days=90)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '6months':
        date_from = datetime.now() - timedelta(days=180)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '1year':
        date_from = datetime.now() - timedelta(days=365)
        news = news.filter(created_at__gte=date_from)
    
    # Сортировка
    sort_filter = request.GET.get('sort', 'newest')
    if sort_filter == 'newest':
        news = news.order_by('-created_at')
    elif sort_filter == 'oldest':
        news = news.order_by('created_at')
    elif sort_filter == 'title':
        news = news.order_by('title')
    
    # Пагинация
    paginator = Paginator(news, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Категории для фильтра
    categories = NewsCategory.objects.filter(type='expert')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'period_filter': period_filter,
        'sort_filter': sort_filter,
    }
    
    return render(request, 'expert_blog/expert_blog_list.html', context)

def expert_blog_detail(request, pk):
    article = get_object_or_404(News, pk=pk, is_published=True, is_expert_news=True)
    
    context = {
        'article': article,
        'expert': article.expert,
        'category': article.category,
    }
    
    return render(request, 'expert_blog/expert_blog_detail.html', context)



def guide_list(request):
    news = News.objects.filter(is_published=True, is_guide=True)
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        news = news.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Фильтр по категории
    category_filter = request.GET.get('category', '')
    if category_filter and category_filter != 'all':
        news = news.filter(category__slug=category_filter)
    
    # Фильтр по периоду
    period_filter = request.GET.get('period', '3months')
    if period_filter == '1month':
        date_from = datetime.now() - timedelta(days=30)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '3months':
        date_from = datetime.now() - timedelta(days=90)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '6months':
        date_from = datetime.now() - timedelta(days=180)
        news = news.filter(created_at__gte=date_from)
    elif period_filter == '1year':
        date_from = datetime.now() - timedelta(days=365)
        news = news.filter(created_at__gte=date_from)
    
    # Сортировка
    sort_filter = request.GET.get('sort', 'newest')
    if sort_filter == 'newest':
        news = news.order_by('-created_at')
    elif sort_filter == 'oldest':
        news = news.order_by('created_at')
    elif sort_filter == 'title':
        news = news.order_by('title')
    
    # Пагинация
    paginator = Paginator(news, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Категории для фильтра
    categories = NewsCategory.objects.filter(type='guide')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'period_filter': period_filter,
        'sort_filter': sort_filter,
    }
    
    return render(request, 'guide/guide_list.html', context)

def guide_detail(request, pk):
    article = get_object_or_404(News, pk=pk, is_published=True, is_guide=True)
    
    context = {
        'article': article,
        'category': article.category,
    }
    
    return render(request, 'guide/guide_detail.html', context)

def partner_shop(request):
    # Фильтры
    partner_filter = request.GET.get('partner', '')
    
    products = Product.objects.all().select_related('partner')
    
    # Применяем фильтры
    if partner_filter:
        products = products.filter(partner__slug=partner_filter)
    
    # Пагинация
    paginator = Paginator(products, 12)  # 12 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Данные для фильтров
    partners = Partner.objects.all()
    
    context = {
        'page_obj': page_obj,
        'partners': partners,
        'partner_filter': partner_filter,
    }
    
    return render(request, 'partners/partner_shop.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'partners/product_detail.html', {'product': product})

def partners(request):
    locale = translation.get_language()
    
    context = {
        'current_language': locale,
        'partners_page': PartnersPageSettings.get_solo(),
    }
    return render(request, 'partners/partners.html', context)