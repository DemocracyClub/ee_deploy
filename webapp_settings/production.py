from .base import *
from ec2_tag_conditional.util import InstanceTags
import raven
import socket


def get_env():
    tags = InstanceTags()
    server_env = None
    if tags['Env']:
        server_env = tags['Env']

    if server_env not in ['test', 'prod', 'packer-ami-build']:
        # if we can't work out our environment, don't attempt to guess
        # fail to bootstrap the application and complain loudly about it
        raise Exception('Failed to infer a valid environment')
    return server_env


# settings that are the same across all instance types

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = '{{ vault_SECRET_KEY }}'

RAVEN_CONFIG = {
    'dsn': '{{ vault_sentry_dsn }}',
}
INSTALLED_APPS.append('raven.contrib.django.raven_compat')
LOGGING['handlers']['sentry'] = {
    'level': 'WARNING',
    'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
}
LOGGING['loggers']['elections.query_helpers'] = {
    'level': 'WARNING',
    'handlers': ['sentry'],
    'propagate': False,
}

ADMINS = (
    ('Sym Roe', 'developers+{{ project_name }}@democracyclub.org.uk'),
)
MANAGERS = ADMINS

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
PIPELINE['SASS_BINARY'] = "/var/www/{{ project_name }}/env/bin/sassc"
PIPELINE['JS_COMPRESSOR'] = "pipeline.compressors.jsmin.JSMinCompressor"

GCS_API_KEY = '{{ vault_GCS_API_KEY }}'

AWS_ACCESS_KEY_ID = '{{ vault_AWS_ACCESS_KEY_ID }}'
AWS_SECRET_ACCESS_KEY = '{{ vault_AWS_SECRET_ACCESS_KEY }}'

EMAIL_SIGNUP_API_KEY = '{{ vault_EMAIL_SIGNUP_API_KEY }}'


DEFAULT_FROM_EMAIL = 'everyelection@democracyclub.org.uk'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_HOST = 'email-smtp.eu-west-1.amazonaws.com'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '{{ vault_smtp_username }}'
EMAIL_HOST_PASSWORD = '{{ vault_smtp_password }}'


# infer environment from the EC2 tags
SERVER_ENVIRONMENT = get_env()


# settings that are conditional on env

RAVEN_CONFIG['environment'] = SERVER_ENVIRONMENT


local_ip_addresses = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())[1] for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]]
if SERVER_ENVIRONMENT == 'packer-ami-build':
    ALLOWED_HOSTS = ['*']
if SERVER_ENVIRONMENT == 'test':
    ALLOWED_HOSTS = local_ip_addresses + [
        "stage.elections.democracyclub.org.uk",
    ]
if SERVER_ENVIRONMENT == 'prod':
    ALLOWED_HOSTS = local_ip_addresses + [
        "elections.democracyclub.org.uk",
        "www.elections.democracyclub.org.uk",
    ]


if SERVER_ENVIRONMENT == 'packer-ami-build':
    DATABASES = {}
if SERVER_ENVIRONMENT in ['prod', 'test']:
    DATABASES = {
        # read/write primary instance
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': '',
            'USER': '{{ project_name }}',
            'PASSWORD': '{{ vault_DATABASE_PASSWORD }}',
            'HOST': '{{ vault_DEFAULT_DATABASE_HOST }}',
            'PORT': '5432',
        },
        # additional capacity for serving API reads
        # if we only want one instance, we can alias
        # vault_REPLICAS_DATABASE_HOST to vault_DEFAULT_DATABASE_HOST
        # with a single CNAME in Route53
        'replicas': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': '',
            'USER': '{{ project_name }}',
            'PASSWORD': '{{ vault_DATABASE_PASSWORD }}',
            'HOST': '{{ vault_REPLICAS_DATABASE_HOST }}',
            'PORT': '5432',
        }
    }
    if SERVER_ENVIRONMENT == 'prod':
        DATABASES['default']['NAME'] = '{{ project_name }}'
        DATABASES['replicas']['NAME'] = '{{ project_name }}'
    if SERVER_ENVIRONMENT == 'test':
        DATABASES['default']['NAME'] = '{{ staging_db_name }}'
        DATABASES['replicas']['NAME'] = '{{ staging_db_name }}'
    DATABASE_ROUTERS = ["every_election.db_routers.DbRouter"]


if SERVER_ENVIRONMENT == 'prod':
    SLACK_WEBHOOK_URL = '{{ vault_SLACK_WEBHOOK_URL }}'


if SERVER_ENVIRONMENT == 'test':
    BASICAUTH_DISABLE = False
    BASICAUTH_REALM = 'Staging'
    BASICAUTH_USERS = {
        'staging': 'staging'
    }
    BASICAUTH_ALWAYS_ALLOW_URLS = [
        r'^/reference_definition/$',
        # Django Rest Framework does not play nicely with django-basicauth
        # TODO: can we fix this?
        r'^/api/.*$',
    ]
