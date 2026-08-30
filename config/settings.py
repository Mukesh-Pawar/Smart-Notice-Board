import os

from pathlib import Path

from urllib.parse import (
    urlparse
)

from dotenv import load_dotenv


BASE_DIR = Path(
    __file__
).resolve().parent.parent


load_dotenv(
    BASE_DIR / '.env'
)


SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'dev-only-change-me'
)


DEBUG = (
    os.getenv(
        'DEBUG',
        'True'
    ).lower()
    in {
        '1',
        'true',
        'yes',
        'on'
    }
)


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.100',
]


INSTALLED_APPS = [

    'django.contrib.admin',

    'django.contrib.auth',

    'django.contrib.contenttypes',

    'django.contrib.sessions',

    'django.contrib.messages',

    'django.contrib.staticfiles',

    'rest_framework',

    'rest_framework.authtoken',

    'accounts',

    'notices',

    'api',
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
]


ROOT_URLCONF = 'config.urls'


TEMPLATES = [

    {

        'BACKEND':
            'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates'
        ],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

            ],

        },

    },

]


WSGI_APPLICATION = (
    'config.wsgi.application'
)


ASGI_APPLICATION = (
    'config.asgi.application'
)


DATABASE_URL = os.getenv(
    'DATABASE_URL',
    ''
).strip()


if DATABASE_URL and DATABASE_URL.startswith(
    (
        'postgres://',
        'postgresql://'
    )
):

    parsed = urlparse(
        DATABASE_URL
    )

    DATABASES = {

        'default': {

            'ENGINE':
                'django.db.backends.postgresql',

            'NAME':
                parsed.path.lstrip('/'),

            'USER':
                parsed.username or '',

            'PASSWORD':
                parsed.password or '',

            'HOST':
                parsed.hostname or '',

            'PORT':
                str(parsed.port or 5432),

        }

    }


elif DATABASE_URL and DATABASE_URL.startswith(
    (
        'mysql://',
        'mysql+mysqlclient://'
    )
):

    parsed = urlparse(
        DATABASE_URL.replace(
            'mysql+mysqlclient://',
            'mysql://',
            1
        )
    )

    DATABASES = {

        'default': {

            'ENGINE':
                'django.db.backends.mysql',

            'NAME':
                parsed.path.lstrip('/'),

            'USER':
                parsed.username or '',

            'PASSWORD':
                parsed.password or '',

            'HOST':
                parsed.hostname or '',

            'PORT':
                str(parsed.port or 3306),

        }

    }


else:

    DATABASES = {

        'default': {

            'ENGINE':
                'django.db.backends.sqlite3',

            'NAME':
                BASE_DIR / 'db.sqlite3',

        }

    }


AUTH_USER_MODEL = 'accounts.User'


AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
    },

    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator',

        'OPTIONS': {
            'min_length': 8
        }
    },

    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
    },

    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
    },

]


LANGUAGE_CODE = 'en-us'


TIME_ZONE = 'Asia/Kolkata'


USE_I18N = True


USE_TZ = True


STATIC_URL = 'static/'


STATICFILES_DIRS = [
    BASE_DIR / 'static'
]


STATIC_ROOT = (
    BASE_DIR / 'staticfiles'
)


MEDIA_URL = 'media/'


MEDIA_ROOT = (
    BASE_DIR / 'media'
)


STORAGES = {

    'default': {

        'BACKEND':
            'django.core.files.storage.'
            'FileSystemStorage',

    },

    'staticfiles': {

        'BACKEND':
            'whitenoise.storage.'
            'CompressedManifestStaticFilesStorage',

    },

}


DEFAULT_AUTO_FIELD = (
    'django.db.models.BigAutoField'
)


LOGIN_URL = (
    'accounts:login'
)


LOGIN_REDIRECT_URL = (
    'accounts:dashboard'
)


LOGOUT_REDIRECT_URL = (
    'accounts:login'
)


SESSION_COOKIE_AGE = int(
    os.getenv(
        'SESSION_COOKIE_AGE',
        '1800'
    )
)


SESSION_EXPIRE_AT_BROWSER_CLOSE = True


SESSION_COOKIE_HTTPONLY = True


SESSION_COOKIE_SAMESITE = 'Lax'


CSRF_COOKIE_HTTPONLY = False


CSRF_COOKIE_SAMESITE = 'Lax'


SECURE_CONTENT_TYPE_NOSNIFF = True


X_FRAME_OPTIONS = 'DENY'


SECURE_REFERRER_POLICY = (
    'same-origin'
)


if not DEBUG:

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

else:

    SESSION_COOKIE_SECURE = False

    CSRF_COOKIE_SECURE = False


EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)


EMAIL_HOST = os.getenv(
    'EMAIL_HOST',
    ''
)


EMAIL_PORT = int(
    os.getenv(
        'EMAIL_PORT',
        '587'
    )
)


EMAIL_HOST_USER = os.getenv(
    'EMAIL_HOST_USER',
    ''
)


EMAIL_HOST_PASSWORD = os.getenv(
    'EMAIL_HOST_PASSWORD',
    ''
)


EMAIL_USE_TLS = (
    os.getenv(
        'EMAIL_USE_TLS',
        'True'
    ).lower()
    in {
        '1',
        'true',
        'yes',
        'on'
    }
)


DEFAULT_FROM_EMAIL = os.getenv(
    'DEFAULT_FROM_EMAIL',
    'no-reply@smartnotice.local'
)


REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [

        'rest_framework.authentication.TokenAuthentication',

        'rest_framework.authentication.SessionAuthentication',

    ],

    'DEFAULT_PERMISSION_CLASSES': [

        'rest_framework.permissions.IsAuthenticated',

    ],

    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',

    'PAGE_SIZE': 10,
}