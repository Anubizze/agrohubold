from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Compile translations and reload WSGI'

    def handle(self, *args, **options):
        os.system(f'cd "{settings.BASE_DIR}" && python manage.py compilemessages')
        wsgi_path = settings.BASE_DIR / 'agrohub' / 'wsgi.py'
        if wsgi_path.exists():
            os.utime(wsgi_path, None)
        self.stdout.write(self.style.SUCCESS('Done'))
