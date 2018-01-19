from django.contrib import admin

from .models import RadioProfile, SongRequest


class FavoriteInline(admin.TabularInline):
    model = RadioProfile.favorites.through
    verbose_name = 'favorite'
    verbose_name_plural = 'favorites'
    extra = 0


class RatingInline(admin.TabularInline):
    model = RadioProfile.ratings.through
    verbose_name = 'rating'
    verbose_name_plural = 'ratings'
    extra = 0


@admin.register(RadioProfile)
class ProfileAdmin(admin.ModelAdmin):
    # Edit Form display
    readonly_fields = ('created_date', 'modified_date')
    fieldsets = (
        ('Main', {
            'fields': ('user',)
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('created_date', 'modified_date')
        })
    )
    can_delete = False
    verbose_name = 'profile'
    verbose_name_plural = 'profiles'
    extra = 0

    inlines = [FavoriteInline, RatingInline]


@admin.register(SongRequest)
class RequestAdmin(admin.ModelAdmin):
    model = SongRequest
    verbose_name = 'request'
    verbose_name_plural = 'requests'
    extra = 0
