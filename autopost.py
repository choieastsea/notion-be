import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from api.pages.models import Page
from api.pages.db import createPage

for i in range(100):
    createPage(Page(title=i, content=i), i - 1)