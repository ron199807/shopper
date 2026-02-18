from django.contrib import admin
from .models import User, UserActivity  # or whatever your model is called

admin.site.register(User)
admin.site.register(UserActivity)