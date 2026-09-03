import secrets

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def populate_tracking_tokens(apps, schema_editor):
    ServiceRequest = apps.get_model('main_app', 'ServiceRequest')
    for request_obj in ServiceRequest.objects.all():
        if not request_obj.tracking_token:
            request_obj.tracking_token = secrets.token_urlsafe(32)
            request_obj.save(update_fields=['tracking_token'])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main_app', '0014_seed_page_cms_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='client_type',
            field=models.CharField(
                choices=[('individual', 'Физическое лицо'), ('legal', 'Юридическое лицо')],
                default='individual',
                max_length=20,
                verbose_name='Тип клиента',
            ),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='company_bin',
            field=models.CharField(blank=True, max_length=200, verbose_name='БИН / компания'),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='tracking_token',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='service_requests',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Пользователь',
            ),
        ),
        migrations.RunPython(populate_tracking_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='servicerequest',
            name='tracking_token',
            field=models.CharField(blank=True, max_length=64, unique=True),
        ),
    ]
