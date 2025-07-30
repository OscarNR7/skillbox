import os

env = os.environ.get('DJANGO_ENVIRONMENT', 'dev')

if env == 'prod':
    from .prod import *
else:
    from .dev import *
