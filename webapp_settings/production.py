from .base import PIPELINE
import socket


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Sym Roe', 'developers+{{ project_name }}@democracyclub.org.uk'),
)
MANAGERS = ADMINS

local_ip_addresses = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())[1] for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]]
ALLOWED_HOSTS = local_ip_addresses + [
    "elections.democracyclub.org.uk",
    "www.elections.democracyclub.org.uk",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '{{ project_name }}',
        'USER': '{{ project_name }}',
        'PASSWORD': '{{ vault_DATABASE_PASSWORD }}',
        'HOST': '{{ vault_DATABASE_HOST }}',
        'PORT': '5432',
    }
}

PIPELINE['SASS_BINARY'] = "/var/www/{{ project_name }}/env/bin/sassc"
PIPELINE['JS_COMPRESSOR'] = "pipeline.compressors.jsmin.JSMinCompressor"

GCS_API_KEY = '{{ vault_GCS_API_KEY }}'

SLACK_WEBHOOK_URL = '{{ vault_SLACK_WEBHOOK_URL }}'

AWS_ACCESS_KEY_ID = '{{ vault_AWS_ACCESS_KEY_ID }}'
AWS_SECRET_ACCESS_KEY = '{{ vault_AWS_SECRET_ACCESS_KEY }}'

EMAIL_SIGNUP_API_KEY = '{{ vault_EMAIL_SIGNUP_API_KEY }}'
