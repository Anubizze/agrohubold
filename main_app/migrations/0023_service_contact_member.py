from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0022_seed_innovation_office'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='contact_member',
            field=models.ForeignKey(
                blank=True,
                help_text='Фото, ФИО и должность подтягиваются из реестра команды.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='services',
                to='main_app.teammember',
                verbose_name='Контактное лицо (реестр команды)',
            ),
        ),
    ]
