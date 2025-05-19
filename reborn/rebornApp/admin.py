#rebornApp/admin.py

from django.contrib import admin
from .models import Item, Category  # Correct import from current app

admin.site.register(Item)
admin.site.register(Category)