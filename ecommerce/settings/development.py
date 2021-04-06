from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', '192.168.43.159']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
WSGI_APPLICATION = 'ecommerce.wsgi.dev.application'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

STRIPE_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY')
