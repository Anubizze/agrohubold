from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0017_projectinfopanel'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='client_iin',
            field=models.CharField(blank=True, max_length=12, verbose_name='ИИН'),
        ),
    ]
