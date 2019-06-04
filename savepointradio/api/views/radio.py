from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from profiles.models import RadioProfile, Rating
from radio.models import Album, Artist, Game, Song, Store
from ..permissions import IsAdminOrReadOnly, IsAuthenticatedAndNotDJ
from ..serializers.profiles import (BasicProfileSerializer,
                                    BasicSongRatingsSerializer,
                                    RateSongSerializer)
from ..serializers.radio import (AlbumSerializer, ArtistSerializer,
                                 GameSerializer, StoreSerializer,
                                 SongSerializer, SongListSerializer,
                                 SongRetrieveSerializer,
                                 SongArtistsListSerializer,
                                 SongStoresSerializer)


class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = AlbumSerializer

    def get_queryset(self):
        '''
        Only send full data to an admin. All regular users get filtered
        albums.
        '''
        if (self.request.user.is_authenticated and
            self.request.user.is_staff and
            not self.request.user.is_dj):
            return Album.objects.all()
        return Album.music.available()


class ArtistViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ArtistSerializer

    def get_queryset(self):
        '''
        Only send full data to an admin. All regular users get filtered
        artists.
        '''
        if (self.request.user.is_authenticated and
            self.request.user.is_staff and
            not self.request.user.is_dj):
            return Artist.objects.all()
        return Artist.music.available()


class GameViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GameSerializer

    def get_queryset(self):
        '''
        Only send full data to an admin. All regular users get filtered
        games.
        '''
        if (self.request.user.is_authenticated and
            self.request.user.is_staff and
            not self.request.user.is_dj):
            return Game.objects.all()
        return Game.music.available()


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = StoreSerializer


class SongViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        '''
        Only send full data to an admin. All regular users get filtered
        songs.
        '''
        if (self.request.user.is_authenticated and
            self.request.user.is_staff and
            not self.request.user.is_dj):
            return Song.objects.all()
        return Song.music.available_songs()

    def get_serializer_class(self):
        '''
        Choose a different serializer based on what action is chosen.

        (Thanks to https://stackoverflow.com/questions/22616973/)
        '''
        if self.action == 'list':
            return SongListSerializer
        if self.action == 'retrieve':
            return SongRetrieveSerializer
        return SongSerializer

    def _artists_change(self, request, remove=False):
        song = self.get_object()
        serializer = SongArtistsListSerializer(data=request.data)
        if serializer.is_valid():
            artists = Artist.objects.filter(pk__in=serializer.data['artists'])

            for artist in artists:
                if remove:
                    song.artists.remove(artist)
                else:
                    song.artists.add(artist)

            song.save()

            if song.artists.count() == 0:
                song.disable('No artists specified for song.')

            message = 'Artists {} song.'.format(('added to',
                                                 'removed from')[remove])
            return Response({'detail': message})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def artists_add(self, request, pk=None):
        '''Adds an artist to a song.'''
        return self._artists_change(request)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def artists_remove(self, request, pk=None):
        '''Removes an artist from a song.'''
        return self._artists_change(request, remove=True)

    def _store_change(self, request, remove=False):
        song = self.get_object()
        serializer = SongStoresSerializer(data=request.data)
        if serializer.is_valid():
            try:
                store = Store.objects.get(pk=serializer.data['store'])
            except Store.DoesNotExist:
                return Response({'detail': 'Store does not exist.'},
                                status=status.HTTP_400_BAD_REQUEST)

            if remove:
                song.stores.remove(store)
            else:
                song.stores.add(store)

            if serializer.data['set_active'] and not remove:
                song.active_store = store

            song.save()

            if song.stores.count() == 0:
                song.disable('No stores specified for song.')

            message = 'Store {} song.'.format(('added to',
                                               'removed from')[remove])
            return Response({'detail': message})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def store_add(self, request, pk=None):
        '''Adds a data store to a song.'''
        return self._store_change(request)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def store_remove(self, request, pk=None):
        '''Removes a data store from a song.'''
        return self._store_change(request, remove=True)

    @action(detail=True, permission_classes=[IsAdminUser])
    def stores(self, request, pk=None):
        '''Get a list of data stores associate with this song.'''
        song = self.get_object()
        stores = song.stores.all().order_by('-created_date')

        page = self.paginate_queryset(stores)
        if page is not None:
            serializer = StoreSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)

    @action(detail=True, permission_classes=[AllowAny])
    def favorites(self, request, pk=None):
        '''Get a list of users who added this song to their favorites list.'''
        song = self.get_object()
        profiles = song.song_favorites.all().order_by('user__name')

        page = self.paginate_queryset(profiles)
        if page is not None:
            serializer = BasicProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BasicProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAuthenticatedAndNotDJ])
    def favorite(self, request, pk=None):
        '''Add a song to the user's favorites list.'''
        song = self.get_object()
        profile = RadioProfile.objects.get(user=request.user)
        if song not in profile.favorites.all():
            profile.favorites.add(song)
            profile.save()
            return Response({'detail': 'Song has been added to favorites.'})
        message = 'Song is already a favorite.'
        return Response({'detail': message},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAuthenticatedAndNotDJ])
    def unfavorite(self, request, pk=None):
        '''Remove a song from the user's favorites list.'''
        song = self.get_object()
        profile = RadioProfile.objects.get(user=request.user)
        if song in profile.favorites.all():
            profile.favorites.remove(song)
            profile.save()
            message = 'Song has been removed from favorites.'
            return Response({'detail': message})
        message = 'Song is already not a favorite.'
        return Response({'detail': message},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=[AllowAny])
    def ratings(self, request, pk=None):
        '''Get a list of a song's ratings.'''
        song = self.get_object()
        ratings = song.rating_set.all().order_by('-created_date')

        page = self.paginate_queryset(ratings)
        if page is not None:
            serializer = BasicSongRatingsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BasicSongRatingsSerializer(ratings, many=True)
        return Response(serializer.data)

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAuthenticatedAndNotDJ])
    def rate(self, request, pk=None):
        '''Add a user's rating to a song.'''
        serializer = RateSongSerializer(data=request.data)
        if serializer.is_valid():
            song = self.get_object()
            profile = RadioProfile.objects.get(user=request.user)
            if 'value' in serializer.data:
                rating, created = Rating.objects.update_or_create(
                    profile=profile,
                    song=song,
                    defaults={'value': serializer.data['value']}
                )
                message = 'Rating {} song.'.format(('updated for',
                                                    'created for')[created])
                return Response({'detail': message})
            message = 'Missing integer \'value\' for song rating.'
            return Response({'detail': message},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAuthenticatedAndNotDJ])
    def unrate(self, request, pk=None):
        '''Remove a user's rating from a song.'''
        song = self.get_object()
        profile = RadioProfile.objects.get(user=request.user)
        rating = song.rating_set.filter(profile=profile)
        if rating:
            rating.delete()
            return Response({'detail': 'Rating deleted from song.'})
        message = 'Cannot delete nonexistant rating.'
        return Response({'detail': message},
                        status=status.HTTP_400_BAD_REQUEST)
