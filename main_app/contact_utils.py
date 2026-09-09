from .models import (
    EngineeringPageSettings,
    InnovationOfficeSettings,
    LabPageSettings,
    ServiceCategory,
    ServiceProvider,
)


def entity_to_contact_column(title='', org='', division='', address='', email='', phone='', person=''):
    lines = []
    if org:
        lines.append(org)
    if person:
        lines.append(f'Контактное лицо: {person}')
    if division:
        lines.append(division)
    if address:
        lines.append(address)
    if email:
        lines.append(f'Email: {email}' if '@' in email and not email.lower().startswith('email') else email)
    if phone:
        lines.append(f'Телефон: {phone}' if phone.replace('+', '').replace(' ', '').isdigit() else phone)
    return {
        'title': title,
        'lines': lines,
        'email': email,
        'phone': phone,
    }


def _page_settings_contact(title, page):
    return entity_to_contact_column(
        title=title,
        org='НАО «Shakarim University»',
        address=getattr(page, 'address_text', '') or '',
        email=getattr(page, 'email_text', '') or '',
        phone=getattr(page, 'phone_text', '') or '',
    )


def provider_to_contact_column(provider):
    if any([provider.contact_email, provider.contact_phone, provider.contact_address, provider.contact_division]):
        return entity_to_contact_column(
            title=provider.name,
            org=provider.contact_org or 'НАО «Shakarim University»',
            division=provider.contact_division,
            address=provider.contact_address,
            email=provider.contact_email,
            phone=provider.contact_phone,
        )

    slug = (provider.slug or '').lower()
    if slug in {'lab', 'shakarim-lab', 'shakarimlab'}:
        return _page_settings_contact(provider.name, LabPageSettings.get_solo())
    if slug in {'engineering', 'engeneering', 'engineering-center', 'inzheniring'}:
        return _page_settings_contact(provider.name, EngineeringPageSettings.get_solo())
    if slug in {'agrotehnopark', 'agro-tehnopark', 'agro'}:
        lab = LabPageSettings.get_solo()
        return entity_to_contact_column(
            title=provider.name,
            org='НАО «Shakarim University»',
            division=getattr(lab, 'agro_title', '') or provider.name,
            address=getattr(lab, 'address_text', '') or '',
            email=getattr(lab, 'email_text', '') or '',
            phone=getattr(lab, 'phone_text', '') or '',
        )

    return entity_to_contact_column(
        title=provider.name,
        org=provider.contact_org or 'НАО «Shakarim University»',
        division=provider.contact_division,
        address=provider.contact_address,
        email=provider.contact_email,
        phone=provider.contact_phone,
    )


def innovation_office_contact_column():
    office = InnovationOfficeSettings.get_solo()
    return entity_to_contact_column(
        title=office.title or 'Офис инноваций',
        org=office.organization or 'НАО «Shakarim University»',
        division=office.division,
        address=office.address,
        email=office.email,
        phone=office.phone,
    )


def get_service_catalog_contact_columns(services_qs, provider_filter='', category_filter=''):
    providers = []

    if category_filter:
        category = ServiceCategory.objects.filter(slug=category_filter, is_active=True).select_related('provider').first()
        if category:
            providers = [category.provider]

    if not providers and provider_filter and provider_filter != 'all':
        provider = ServiceProvider.objects.filter(slug=provider_filter, is_active=True).first()
        if provider:
            providers = [provider]

    if not providers:
        provider_ids = services_qs.values_list('category__provider_id', flat=True).distinct()
        providers = list(
            ServiceProvider.objects.filter(id__in=provider_ids, is_active=True).order_by('name')
        )

    columns = [provider_to_contact_column(provider) for provider in providers]
    columns.append(innovation_office_contact_column())
    return columns


def has_contact_content(column):
    return bool(column and (column.get('lines') or column.get('email') or column.get('phone')))
