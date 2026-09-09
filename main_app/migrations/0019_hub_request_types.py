from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0018_servicerequest_client_iin'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='request_attachments/', verbose_name='Вложение'),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='category',
            field=models.CharField(
                blank=True,
                choices=[
                    ('SERVICE', 'Услуга'),
                    ('PROJECT', 'Проект / технология'),
                    ('LABORATORY', 'Лаборатория / научный центр'),
                    ('EDUCATION', 'Образование'),
                    ('OTHER', 'Другое'),
                ],
                max_length=20,
                verbose_name='Категория интереса',
            ),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ID объекта'),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='object_title',
            field=models.CharField(blank=True, max_length=300, verbose_name='Название объекта'),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='object_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('SERVICE', 'Service'),
                    ('PROJECT', 'Project'),
                    ('LABORATORY', 'Laboratory'),
                ],
                max_length=20,
                verbose_name='Тип объекта',
            ),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='proposal_title',
            field=models.CharField(blank=True, max_length=300, verbose_name='Название предлагаемого проекта'),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='project',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='collaboration_requests',
                to='main_app.project',
                verbose_name='Проект',
            ),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='request_type',
            field=models.CharField(
                choices=[
                    ('SERVICE', 'Service Request'),
                    ('PROJECT', 'Project Collaboration'),
                    ('PROJECT_PROPOSAL', 'Project Proposal'),
                    ('GENERAL', 'General Request'),
                ],
                db_index=True,
                default='SERVICE',
                max_length=20,
                verbose_name='Тип заявки',
            ),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='source_page',
            field=models.CharField(blank=True, max_length=500, verbose_name='Страница отправки'),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='services',
            field=models.ManyToManyField(blank=True, related_name='requests', to='main_app.service'),
        ),
        migrations.AlterModelOptions(
            name='servicerequest',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Hub Request',
                'verbose_name_plural': 'Hub Requests',
            },
        ),
    ]
