from django.contrib import admin
from .models import System_users, UserInformation, Professor

admin.site.register(System_users)
admin.site.register(UserInformation)
admin.site.register(Professor)
