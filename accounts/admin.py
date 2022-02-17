from django.contrib import admin
from .models import Accounts
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'last_login', 'date_joined')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter=()
    fieldsets=()

admin.site.register(Accounts, AccountAdmin)
