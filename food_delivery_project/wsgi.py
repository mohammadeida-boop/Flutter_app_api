"""
WSGI config for food_delivery_project project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from whitenoise import WhiteNoise

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery_project.settings')

application = get_wsgi_application()

# Apply WhiteNoise middleware for static files
application = WhiteNoise(application)