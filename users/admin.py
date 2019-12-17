from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'hours']
    fieldsets = (
        (('User'), {'fields': ('username','hours', 'email','lastteacher','timeoffset', 'is_staff', 'city')}),
    )
    readonly_fields = ['hours']
    #fields = ['username', 'email', 'is_staff', 'hours']
    # https://developer.mozilla.org/ru/docs/Learn/Server-side/Django/Admin_site
    # by https://stackoverflow.com/questions/53355638/django-custom-user-edit-new-customuser-fields-in-admin


admin.site.register(CustomUser, CustomUserAdmin)
