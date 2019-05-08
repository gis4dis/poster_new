from urllib.parse import urlparse
import environ
import os
import sys
import apps.mc.settings as MC_SETTINGS

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    import apps.mc.settings_test as MC_SETTINGS

# Basic environ configuration to get all environment variables

root = environ.Path(__file__) - 2            # two folder back (/a/b/c/ - 2 = /a/)
env = environ.Env(DJANGO_DEBUG=(bool, False),)      # set default values and casting
# environ.Env.read_env(env_file=root('.env'))  # reading .env file

BASE_DIR = root()

# Configuration obtained from environment variables

DEBUG = env.bool('DJANGO_DEBUG')
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = env('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS', default='').split(',')

# STATIC_ROOT = env('DJANGO_STATIC_ROOT', default='/static')
STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
STATIC_URL = env('DJANGO_STATIC_URL', default='/static/')
MEDIA_ROOT = env('DJANGO_MEDIA_ROOT', default='/media')
MEDIA_URL = env('DJANGO_MEDIA_URL', default='/media/')


DATABASES = {
    'default': env.db(engine='django.contrib.gis.db.backends.postgis')
}
# https://github.com/joke2k/django-environ/issues/175
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

REDIS_URL = env('REDIS_URL', default=None)

# CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=None) or REDIS_URL

# CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=None) or REDIS_URL

DEFAULT_FILE_STORAGE = env('DJANGO_DEFAULT_FILE_STORAGE', default='django.core.files.storage.FileSystemStorage')

if DEFAULT_FILE_STORAGE == 'minio_storage.storage.MinioMediaStorage':
    MINIO_STORAGE_ENDPOINT = env('MINIO_STORAGE_ENDPOINT')
    MINIO_STORAGE_ACCESS_KEY = env('MINIO_STORAGE_ACCESS_KEY')
    MINIO_STORAGE_SECRET_KEY = env('MINIO_STORAGE_SECRET_KEY')
    MINIO_STORAGE_USE_HTTPS = env.bool('MINIO_STORAGE_USE_HTTPS')
    MINIO_STORAGE_MEDIA_BUCKET_NAME = env('MINIO_STORAGE_MEDIA_BUCKET_NAME')
    MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = env.bool('MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET')
    MINIO_STORAGE_MEDIA_URL = "/files/"


# Custom configuration - from env
APPLICATION_PMO_FTP_URL = urlparse(env('APPLICATION_PMO_FTP_URL', default=None))
APPLICATION_O2_API_KEY = env('APPLICATION_O2_API_KEY', default=None)
APPLICATION_MC = MC_SETTINGS

# Custom configuration
CELERY_TIMEZONE = 'Etc/GMT-1'   # Due to https://github.com/celery/celery/issues/4184, https://github.com/celery/django-celery-beat/issues/109
CELERY_ENABLE_UTC = True  # Due to https://github.com/celery/celery/issues/4184
ALLOWED_EXTENSIONS = ['json', 'xml', 'txt']  # importing of data
IMPORT_ROOT = "import/"  # inside a media bucket
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'  # Whitenoise is server staticfiles wrapper

LOG_LEVEL = env('DJANGO_LOG_LEVEL', default='ERROR')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    'sekizai',
    'widget_tweaks',

    'rest_framework',
    'rest_framework_gis',

    'django.contrib.humanize',
    'django.contrib.gis',

    'django_celery_beat',
    'django_celery_results',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',

    'apps.social_auth_addons',

    'apps.common',
    'apps.utils',
    'apps.mc',

    'apps.importing',

    'apps.processing.ala',
    'apps.processing.pmo',
    'apps.processing.o2',
    'apps.processing.rsd',
    'apps.processing.ozp',

    'debug_toolbar',
    'django_extensions',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'poster.urls'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),  # Base static path
    os.path.join(BASE_DIR, "modules/mc-client/out/static"),  # Map client git submodule
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),  # Basic template folder
            os.path.join(BASE_DIR, "modules/mc-client/out/static")  # Map client git submodule
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
            ],
        },
    },
]

WSGI_APPLICATION = 'poster.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_ADAPTER = 'poster.account_adapter.NoNewUsersAccountAdapter'

LOGIN_REDIRECT_URL = "/"

SITE_ID = 1

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Etc/GMT-1'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
        },
    },
}

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False
}


def show_toolbar(request):
    return DEBUG


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}


if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
}

NOTEBOOK_ARGUMENTS = [
    '--ip', '0.0.0.0',
    '--port', env('PORT', default='8888'),
    '--notebook-dir', './jupyter-notebooks/',
    '--allow-root',
]
