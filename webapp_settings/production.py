from .base import *
from ec2_tag_conditional.util import InstanceTags
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


# infer environment from the EC2 tags
SERVER_ENVIRONMENT = get_env()


# settings that are conditional on env

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
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': '',
            'USER': '{{ project_name }}',
            'PASSWORD': '{{ vault_DATABASE_PASSWORD }}',
            'HOST': '{{ vault_DATABASE_HOST }}',
            'PORT': '5432',
        }
    }
    if SERVER_ENVIRONMENT == 'prod':
        DATABASES['default']['NAME'] = '{{ project_name }}'
    if SERVER_ENVIRONMENT == 'test':
        DATABASES['default']['NAME'] = 'ee_staging'


if SERVER_ENVIRONMENT == 'prod':
    SLACK_WEBHOOK_URL = '{{ vault_SLACK_WEBHOOK_URL }}'
