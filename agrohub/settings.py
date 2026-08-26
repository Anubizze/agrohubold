import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '+!9cpr#&)1!wn$k@)4wmai*87n95z2)664z5191)+#iu)^cy5q'

DEBUG = False

ALLOWED_HOSTS = ['agrohub.shakarim.kz']

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rosetta',
    'main_app.apps.MainAppConfig',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'agrohub.custom_locale.CustomLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agrohub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'agrohub.wsgi.application'

DATABASES = {
    'default': {
        "ENGINE": 'django.db.backends.mysql',
        "NAME": 'agrohub_db',
        "USER": 'agrohub_user',
        "PASSWORD": '?Xv1e859/BN,',
        "HOST": 'localhost',
        "PORT": '3306',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru'
LANGUAGE_SESSION_KEY = 'django_language'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ru', 'Russian'),
    ('kk', 'Kazakh'),
    ('en', 'English'),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('en', 'kk')

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_production')
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'uploads'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOCALE_PATHS = [
    BASE_DIR / 'main_app' / 'locale',
]

ROSETTA_AUTO_COMPILE = True
ROSETTA_WSGI_AUTO_RELOAD = True
ROSETTA_UWSGI_AUTO_RELOAD = True

AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/profile/'

SITE_DOMAIN = os.getenv("SITE_DOMAIN", "https://agrohub.shakarim.kz")
CSRF_TRUSTED_ORIGINS = ['https://agrohub.shakarim.kz']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
