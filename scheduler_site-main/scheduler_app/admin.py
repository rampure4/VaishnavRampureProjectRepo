from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'account_type']


admin.site.register(User, UserAdmin)
