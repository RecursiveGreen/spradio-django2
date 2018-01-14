from django.contrib import admin
from django.db import models
from django.forms import TextInput

from .actions import change_m2m_items, publish_items
from .models import Album, Artist, Game, Song


class ArtistInline(admin.TabularInline):
    model = Song.artists.through
    verbose_name = 'artist'
    verbose_name_plural = 'artists'
    extra = 0


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    # Detail List display
    list_display = ('title', '_is_enabled', '_is_published')
    search_fields = ['title']
    actions = ['publish_albums']

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

    def publish_albums(self, request, queryset):
        publish_items(request, queryset)
    publish_albums.short_description = "Publish selected albums"


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    # Detail List display
    list_display = ('first_name',
                    'alias',
                    'last_name',
                    '_is_enabled',
                    '_is_published')
    search_fields = ['first_name', 'alias', 'last_name']
    actions = ['publish_artists']

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

    def publish_artists(self, request, queryset):
        publish_items(request, queryset)
    publish_artists.short_description = "Publish selected artists"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    # Detail List display
    list_display = ('title', '_is_enabled', '_is_published')
    search_fields = ['title']
    actions = ['publish_games']

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

    def publish_games(self, request, queryset):
        publish_items(request, queryset)
    publish_games.short_description = "Publish selected games"


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size': 160, })},
    }

    # Detail List display
    list_display = ('title',
                    'game',
                    'album',
                    'artist_list',
                    '_is_enabled',
                    '_is_published')
    search_fields = ['title']
    actions = ['publish_songs', 'add_artists', 'remove_artists']

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

    def add_artists(self, request, queryset):
        return change_m2m_items(request, queryset, Song, 'artists',
                                'artist', 'add_artists')
    add_artists.short_description = "Add artists to selected items"

    def remove_artists(self, request, queryset):
        return change_m2m_items(request, queryset, Song, 'artists',
                                'artist', 'remove_artists', remove=True)
    remove_artists.short_description = "Remove artists from selected items"

    def publish_songs(self, request, queryset):
        publish_items(request, queryset)
    publish_songs.short_description = "Publish selected songs"
