from django.conf import settings
if settings.TESTING:
    from .function_test import *
else:
    from .functions_production import *
