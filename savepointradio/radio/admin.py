from django.contrib import admin, messages
from django.db import models
from django.forms import TextInput
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from .forms import ArtistFormSet
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
                    '_is_enabled',
                    '_is_published')
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
    list_display = ('title', '_is_enabled', '_is_published')
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
                    'album',
                    'artist_list',
                    '_is_enabled',
                    '_is_published')
    search_fields = ['title']
    actions = ['publish_items', 'add_artists', 'remove_artists']

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
        artist_formset = None

        # If we clicked "Add Artists", then continue. . .
        if 'apply' in request.POST:
            # Fill the formset with values from the POST request
            artist_formset = ArtistFormSet(request.POST)

            # Will only returned "cleaned_data" if form is valid
            if artist_formset.is_valid():
                # remove the empty form data from the list
                data = list(filter(None, artist_formset.cleaned_data))

                for artist in data:
                    for song in queryset:
                        song.artists.add(artist['artist'])

                # Return with informative success message and counts
                a_count = len(data)
                s_count = queryset.count()
                a_msg = ('1 artist was',
                         '{} artists were'.format(a_count))[a_count > 1]
                s_msg = ('1 song', '{} songs'.format(s_count))[s_count > 1]
                self.message_user(request,
                                  '{} successfully added to {}.'.format(a_msg,
                                                                        s_msg))
                return HttpResponseRedirect(request.get_full_path())
            else:
                self.message_user(request,
                                  "See below for errors in the form.",
                                  level=messages.ERROR)
        # . . .otherwise, create empty formset.
        if not artist_formset:
            artist_formset = ArtistFormSet()

        return render(request,
                      'admin/add_artists_intermediate.html',
                      {'songs': queryset, 'artist_formset': artist_formset, })
    add_artists.short_description = "Add artists to selected items"

    def remove_artists(self, request, queryset):
        artist_formset = None

        # If we clicked "Remove Artists", then continue. . .
        if 'apply' in request.POST:
            # Fill the formset with values from the POST request
            artist_formset = ArtistFormSet(request.POST)

            # Will only returned "cleaned_data" if form is valid
            if artist_formset.is_valid():
                # remove the empty form data from the list
                data = list(filter(None, artist_formset.cleaned_data))

                for artist in data:
                    for song in queryset:
                        song.artists.remove(artist['artist'])

                # Return with informative success message and counts
                a_count = len(data)
                s_count = queryset.count()
                a_msg = ('1 artist was',
                         '{} artists were'.format(a_count))[a_count > 1]
                s_msg = ('1 song', '{} songs'.format(s_count))[s_count > 1]
                self.message_user(request,
                                  '{} successfully removed from {}.'.format(a_msg,
                                                                            s_msg))
                return HttpResponseRedirect(request.get_full_path())
            else:
                self.message_user(request,
                                  "See below for errors in the form.",
                                  level=messages.ERROR)
        # . . .otherwise, create empty formset.
        if not artist_formset:
            artist_formset = ArtistFormSet()

        return render(request,
                      'admin/remove_artists_intermediate.html',
                      {'songs': queryset, 'artist_formset': artist_formset, })
    remove_artists.short_description = "Remove artists from selected items"

    def publish_items(self, request, queryset):
        rows_updated = queryset.update(published_date=timezone.now())
        if rows_updated == 1:
            msg = '1 song was'
        else:
            msg = '{} songs were'.format(str(rows_updated))
        self.message_user(request, '{} successfully published.'.format(msg))
    publish_items.short_description = "Publish selected items"
