# -- encoding: utf-8 --
"""
Django settings for gezusercenter project.

Generated by 'django-admin startproject' using Django 1.9.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import ConfigParser
import os

config_file = ConfigParser.ConfigParser()

config_file.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'd5&d%n$&5&huu8a+%av8cieya@hm0^0^$f*#@mhzy5h3f95_!h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.messages',
    # 'djcelery_email',
    # 'celery',
    'public',
    'rest_framework',
    'django.contrib.staticfiles',
    'usermanager',
    'products',
    'sdk',
    # 'debug_toolbar',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# INTERNAL_IPS = ('127.0.0.1')

ROOT_URLCONF = 'gezusercenter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'gezusercenter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config_file.get('database', 'name'),
        'USER': config_file.get('database', 'username'),
        'PASSWORD': config_file.get('database', 'password'),
        'HOST': config_file.get('database', 'host'),
        'PORT': config_file.get('database', 'port'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/statics-files/

STATIC_URL = '/statics/'
STATIC_FILES = os.path.join(BASE_DIR, 'statics')
STATICFILES_DIRS = (
    STATIC_FILES,
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config_file.get('redis', 'location'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.ShardClient",
            "SOCKET_TIMEOUT": 5,
            "PASSWORD": config_file.get('redis', 'password'),
        }
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"
# SESSION_COOKIE_AGE = 360


# 邮箱配置
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = config_file.get('email', 'host')
EMAIL_PORT = config_file.get('email', 'port')
EMAIL_HOST_USER = config_file.get('email', 'username')
EMAIL_HOST_PASSWORD = config_file.get('email', 'password')
EMAIL_USE_TLS = config_file.get('email', 'tls')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 管理员站点
SERVER_EMAIL = config_file.get('email', 'username')

# 服务器地址
SERVER_WEBSITE = config_file.get('url', 'server_url')
# 官网地址
OFFICIAL_WEBSITE = config_file.get('url', 'offical_url')
# 设计师地址
DESIGNER_WEBSITE = config_file.get('url', 'designer_url')
