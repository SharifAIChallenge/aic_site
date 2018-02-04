from django.conf import settings
if settings.TESTING:
    from .functions_test import *
else:
    from .functions_production import *
