from django.contrib import admin

from authtools.admin import UserAdmin

from .models import RadioUser


@admin.register(RadioUser)
class RadioUserAdmin(UserAdmin):
    pass