from django.contrib import admin
from .models import Accounts, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'last_login', 'date_joined')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter=()
    fieldsets=()

class UserProfileAdmin(admin.ModelAdmin):
    # def image(self, object):
    #     return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    list_display = ('user', 'address', 'country',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Accounts, AccountAdmin)
