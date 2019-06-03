from django.contrib import admin
from django.db import models
from django.forms import TextInput

from .actions import change_items, publish_items, remove_items
from .models import Album, Artist, Game, Song, Store


class ArtistInline(admin.TabularInline):
    model = Song.artists.through
    verbose_name = 'artist'
    verbose_name_plural = 'artists'
    extra = 0


class StoreInline(admin.TabularInline):
    model = Song.stores.through
    verbose_name = 'data store'
    verbose_name_plural = 'data stores'
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


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    # Detail List display
    list_display = ('iri',
                    'mime_type',
                    'file_size',
                    'length')
    search_fields = ['iri']

    # Edit Form display
    readonly_fields = ('created_date', 'modified_date')
    fieldsets = (
        ('Main', {
            'fields': ('iri', 'mime_type', 'file_size', 'length')
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('created_date', 'modified_date')
        })
    )


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
                    '_is_published',
                    '_is_requestable')
    search_fields = ['title']
    actions = ['publish_songs',
               'add_game', 'remove_game',
               'add_album', 'remove_album',
               'add_artists', 'remove_artists']

    # Edit Form display
    exclude = ('artists',)
    readonly_fields = ('last_played',
                       'num_played',
                       'created_date',
                       'modified_date',
                       'next_play')
    fieldsets = (
        ('Song Disabling', {
            'classes': ('collapse',),
            'fields': ('disabled', 'disabled_date', 'disabled_reason')
        }),
        ('Main', {
            'fields': ('song_type',
                       'title',
                       'published_date',
                       'current_store')
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('created_date',
                       'modified_date',
                       'last_played',
                       'num_played',
                       'next_play')
        }),
        ('Album', {
            'fields': ('album',)
        }),
        ('Game', {
            'fields': ('game',)
        })
    )
    inlines = [ArtistInline, StoreInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'current_store':
            kwargs['queryset'] = Store.objects.filter(
                song__pk=request.resolver_match.kwargs['object_id']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def artist_list(self, obj):
        return ', '.join([a.full_name for a in obj.artists.all()])

    def add_album(self, request, queryset):
        return change_items(request, queryset, 'album', 'add_album')
    add_album.short_description = "Add album to selected items"

    def remove_album(self, request, queryset):
        return remove_items(request, queryset, 'album', 'remove_album')
    remove_album.short_description = "Remove album from selected items"

    def add_artists(self, request, queryset):
        return change_items(request, queryset, 'artists', 'add_artists',
                            m2m='artist')
    add_artists.short_description = "Add artists to selected items"

    def remove_artists(self, request, queryset):
        return change_items(request, queryset, 'artists', 'remove_artists',
                            m2m='artist', remove=True)
    remove_artists.short_description = "Remove artists from selected items"

    def add_game(self, request, queryset):
        return change_items(request, queryset, 'game', 'add_game')
    add_game.short_description = "Add game to selected items"

    def remove_game(self, request, queryset):
        return remove_items(request, queryset, 'game', 'remove_game')
    remove_game.short_description = "Remove game from selected items"

    def publish_songs(self, request, queryset):
        publish_items(request, queryset)
    publish_songs.short_description = "Publish selected songs"
