"""WSGI config for financial_simulator project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financial_simulator.settings")

application = get_wsgi_application()
