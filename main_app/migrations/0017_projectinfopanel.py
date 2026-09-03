from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0016_swap_lab_images_and_service_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectInfoPanel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('title_ru', models.CharField(max_length=200, null=True, verbose_name='Заголовок')),
                ('title_kk', models.CharField(max_length=200, null=True, verbose_name='Заголовок')),
                ('title_en', models.CharField(max_length=200, null=True, verbose_name='Заголовок')),
                ('items', models.TextField(help_text='Каждый пункт с новой строки', verbose_name='Пункты списка')),
                ('items_ru', models.TextField(help_text='Каждый пункт с новой строки', null=True, verbose_name='Пункты списка')),
                ('items_kk', models.TextField(help_text='Каждый пункт с новой строки', null=True, verbose_name='Пункты списка')),
                ('items_en', models.TextField(help_text='Каждый пункт с новой строки', null=True, verbose_name='Пункты списка')),
                ('display_mode', models.CharField(
                    choices=[('inline', 'Карточка на странице'), ('modal', 'Модальное окно')],
                    default='inline',
                    max_length=20,
                    verbose_name='Тип отображения',
                )),
                ('trigger_label', models.CharField(blank=True, help_text='Для модального окна. Если пусто — используется заголовок.', max_length=150, verbose_name='Текст кнопки')),
                ('trigger_label_ru', models.CharField(blank=True, help_text='Для модального окна. Если пусто — используется заголовок.', max_length=150, null=True, verbose_name='Текст кнопки')),
                ('trigger_label_kk', models.CharField(blank=True, help_text='Для модального окна. Если пусто — используется заголовок.', max_length=150, null=True, verbose_name='Текст кнопки')),
                ('trigger_label_en', models.CharField(blank=True, help_text='Для модального окна. Если пусто — используется заголовок.', max_length=150, null=True, verbose_name='Текст кнопки')),
                ('accent_color', models.CharField(default='#c91d00', max_length=7, verbose_name='Цвет линии под заголовком')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='info_panels', to='main_app.project', verbose_name='Проект')),
            ],
            options={
                'verbose_name': 'Информационная панель',
                'verbose_name_plural': 'Информационные панели',
                'ordering': ['order', 'id'],
            },
        ),
    ]
