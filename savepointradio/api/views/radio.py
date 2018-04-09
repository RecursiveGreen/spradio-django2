from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from profiles.models import RadioProfile, Rating
from radio.models import Album, Artist, Game, Song
from ..permissions import IsAdminOrReadOnly, IsAuthenticatedAndNotDJ
from ..serializers.profiles import (BasicProfileSerializer,
                                    BasicSongRatingsSerializer,
                                    RateSongSerializer)
from ..serializers.radio import (AlbumSerializer, ArtistSerializer,
                                 GameSerializer, FullSongSerializer,
                                 SongArtistsListSerializer,
                                 FullSongRetrieveSerializer)


class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer


class ArtistViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


class GameViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class SongViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Song.objects.all()

    def get_serializer_class(self):
        '''
        Choose a different serializer based on what action is chosen.

        (Thanks to https://stackoverflow.com/questions/22616973/)
        '''
        if self.action in ['list', 'retrieve']:
            return FullSongRetrieveSerializer
        return FullSongSerializer

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
            message = 'Artists {} song.'.format(('added to',
                                                 'removed from')[remove])
            return Response({'detail': message})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def artists_add(self, request, pk=None):
        return self._artists_change(request)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def artists_remove(self, request, pk=None):
        return self._artists_change(request, remove=True)

    @action(detail=True, permission_classes=[AllowAny])
    def favorites(self, request, pk=None):
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
        song = self.get_object()
        profile = RadioProfile.objects.get(user=request.user)
        rating = song.rating_set.filter(profile=profile)
        if rating:
            rating.delete()
            return Response({'detail': 'Rating deleted from song.'})
        message = 'Cannot delete nonexistant rating.'
        return Response({'detail': message},
                        status=status.HTTP_400_BAD_REQUEST)
