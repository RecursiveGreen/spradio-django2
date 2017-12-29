from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils import timezone

from .models import Album, Artist, Game, Song


class ArtistInline(admin.TabularInline):
    model = Song.artists.through
    verbose_name = 'artist'
    verbose_name_plural = 'artists'
    extra = 0


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    # Detail List display
    list_display = ('title', 'is_enabled', 'is_published')
    search_fields = ['title']
    actions = ['publish_items']

    # Edit Form display
    readonly_fields = ('created_date', 'modified_date')
    fieldsets = (
        ('Album Disabling', {
            'classes': ('collapse',),
            'fields': ('disabled', 'disabled_date', 'disabled_reason')
        }),
        ('Main', {
            'fields': ('title', 'published_date')
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('created_date', 'modified_date')
        })
    )

    def is_enabled(self, obj):
        return not obj.disabled

    def is_published(self, obj):
        return obj.is_published

    def publish_items(self, request, queryset):
        rows_updated = queryset.update(published_date=timezone.now())
        if rows_updated == 1:
            msg = '1 album was'
        else:
            msg = '{} albums were'.format(str(rows_updated))
        self.message_user(request, '{} successfully published.'.format(msg))
    publish_items.short_description = "Publish selected items"


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    # Detail List display
    list_display = ('first_name',
                    'alias',
                    'last_name',
                    'is_enabled',
                    'is_published')
    search_fields = ['first_name', 'alias', 'last_name']
    actions = ['publish_items']

    # Edit Form display
    readonly_fields = ('created_date', 'modified_date')
    fieldsets = (
        ('Artist Disabling', {
            'classes': ('collapse',),
            'fields': ('disabled', 'disabled_date', 'disabled_reason')
        }),
        ('Main', {
            'fields': ('first_name', 'alias', 'last_name', 'published_date')
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('created_date', 'modified_date')
        })
    )

    def is_enabled(self, obj):
        return not obj.disabled

    def is_published(self, obj):
        return obj.is_published

    def publish_items(self, request, queryset):
        rows_updated = queryset.update(published_date=timezone.now())
        if rows_updated == 1:
            msg = '1 artist was'
        else:
            msg = '{} artists were'.format(str(rows_updated))
        self.message_user(request, '{} successfully published.'.format(msg))
    publish_items.short_description = "Publish selected items"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    # Detail List display
    list_display = ('title', 'is_enabled', 'is_published')
    search_fields = ['title']
    actions = ['publish_items']

    # Edit Form display
    readonly_fields = ('created_date', 'modified_date')
    fieldsets = (
        ('Game Disabling', {
            'classes': ('collapse',),
            'fields': ('disabled', 'disabled_date', 'disabled_reason')
        }),
        ('Main', {
            'fields': ('title', 'published_date')
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('created_date', 'modified_date')
        })
    )

    def is_enabled(self, obj):
        return not obj.disabled

    def is_published(self, obj):
        return obj.is_published

    def publish_items(self, request, queryset):
        rows_updated = queryset.update(published_date=timezone.now())
        if rows_updated == 1:
            msg = '1 game was'
        else:
            msg = '{} games were'.format(str(rows_updated))
        self.message_user(request, '{} successfully published.'.format(msg))
    publish_items.short_description = "Publish selected items"


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': 160, })},
    }

    # Detail List display
    list_display = ('title',
                    'game',
                    'artist_list',
                    'is_enabled',
                    'is_published')
    search_fields = ['title']
    actions = ['publish_items']

    # Edit Form display
    exclude = ('artists',)
    readonly_fields = ('length',
                       'last_played',
                       'num_played',
                       'created_date',
                       'modified_date')
    fieldsets = (
        ('Song Disabling', {
            'classes': ('collapse',),
            'fields': ('disabled', 'disabled_date', 'disabled_reason')
        }),
        ('Main', {
            'fields': ('song_type',
                       'title',
                       'path',
                       'published_date')
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('created_date',
                       'modified_date',
                       'last_played',
                       'num_played',
                       'length')
        }),
        ('Album', {
            'fields': ('album',)
        }),
        ('Game', {
            'fields': ('game',)
        })
    )
    inlines = [ArtistInline]

    def artist_list(self, obj):
        return ', '.join([a.full_name for a in obj.artists.all()])

    def is_enabled(self, obj):
        return not obj.disabled

    def is_published(self, obj):
        return obj.is_published

    def publish_items(self, request, queryset):
        rows_updated = queryset.update(published_date=timezone.now())
        if rows_updated == 1:
            msg = '1 song was'
        else:
            msg = '{} songs were'.format(str(rows_updated))
        self.message_user(request, '{} successfully published.'.format(msg))
    publish_items.short_description = "Publish selected items"
