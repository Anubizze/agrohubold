from django.db import migrations


def seed_innovation_office(apps, schema_editor):
    InnovationOfficeSettings = apps.get_model('main_app', 'InnovationOfficeSettings')
    InnovationOfficeSettings.objects.update_or_create(
        pk=1,
        defaults={
            'title': 'Офис инноваций',
            'organization': 'НАО «Shakarim University»',
            'division': 'Подразделение: Научный парк',
            'address': 'Адрес: г. Семей, ул. Глинки 20A',
            'email': 'innovation@shakarim.kz',
            'phone': '+7 777 153 7323',
            'lead': 'По вопросам образования, проектов и общих запросов — свяжитесь с Офисом инноваций.',
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0021_innovationofficesettings_course_contact_address_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_innovation_office, migrations.RunPython.noop),
    ]
