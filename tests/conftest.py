import pytest
import os

# Ensure Django settings are configured before importing anything Django-related
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django

django.setup()