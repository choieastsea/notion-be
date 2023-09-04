import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from api.pages.models import Page
from api.pages.db import createPage

for i in range(100):
    page = Page(title=i, content=i)
    page.save()
    createPage(page, i - 1)