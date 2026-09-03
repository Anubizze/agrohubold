from django.db import migrations


def swap_lab_images_and_fix_service_title(apps, schema_editor):
    LabPageSettings = apps.get_model('main_app', 'LabPageSettings')
    LabServiceCard = apps.get_model('main_app', 'LabServiceCard')

    try:
        lab = LabPageSettings.objects.get(pk=1)
        food_image = lab.food_image
        milk_image = lab.milk_image
        lab.food_image = milk_image
        lab.milk_image = food_image
        lab.save(update_fields=['food_image', 'milk_image'])
    except LabPageSettings.DoesNotExist:
        pass

    replacements = {
        'ru': 'Микробиологические исследования',
        'en': 'Microbiological research',
        'kk': 'Микробиологиялық зерттеулер',
    }
    for card in LabServiceCard.objects.filter(page_id=1):
        titles = [
            card.title,
            getattr(card, 'title_ru', '') or '',
            getattr(card, 'title_en', '') or '',
            getattr(card, 'title_kk', '') or '',
        ]
        if any('Микроскоп' in value or 'Microscop' in value or 'Микроскопия' in value for value in titles):
            card.title = replacements['ru']
            if hasattr(card, 'title_ru'):
                card.title_ru = replacements['ru']
            if hasattr(card, 'title_en'):
                card.title_en = replacements['en']
            if hasattr(card, 'title_kk'):
                card.title_kk = replacements['kk']
            card.save()


def reverse_swap(apps, schema_editor):
    LabPageSettings = apps.get_model('main_app', 'LabPageSettings')
    LabServiceCard = apps.get_model('main_app', 'LabServiceCard')

    try:
        lab = LabPageSettings.objects.get(pk=1)
        food_image = lab.food_image
        milk_image = lab.milk_image
        lab.food_image = milk_image
        lab.milk_image = food_image
        lab.save(update_fields=['food_image', 'milk_image'])
    except LabPageSettings.DoesNotExist:
        pass

    replacements = {
        'ru': 'Микроскопические исследования',
        'en': 'Microscopic Research',
        'kk': 'Микроскопиялық зерттеулер',
    }
    for card in LabServiceCard.objects.filter(page_id=1):
        titles = [
            card.title,
            getattr(card, 'title_ru', '') or '',
            getattr(card, 'title_en', '') or '',
            getattr(card, 'title_kk', '') or '',
        ]
        if any('Микробиолог' in value or 'Microbiolog' in value for value in titles):
            card.title = replacements['ru']
            if hasattr(card, 'title_ru'):
                card.title_ru = replacements['ru']
            if hasattr(card, 'title_en'):
                card.title_en = replacements['en']
            if hasattr(card, 'title_kk'):
                card.title_kk = replacements['kk']
            card.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0015_servicerequest_tracking_fields'),
    ]

    operations = [
        migrations.RunPython(swap_lab_images_and_fix_service_title, reverse_swap),
    ]
