import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# TODO: Configure production database, security settings, etc.
