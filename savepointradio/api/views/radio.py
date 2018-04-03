from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from radio.models import Album, Artist, Game, Song
from ..permissions import IsAdminOrReadOnly
from ..serializers.radio import (AlbumSerializer, ArtistSerializer,
                                 GameSerializer, SongSerializer,
                                 SongArtistsListSerializer,
                                 SongCreateSerializer, SongRetrieveSerializer)


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
    serializer_class = SongSerializer

    def get_serializer_class(self):
        '''
        Choose a different serializer based on what action is chosen.

        (Thanks to https://stackoverflow.com/questions/22616973/)
        '''
        if self.action == 'create':
            return SongCreateSerializer
        if self.action in ['list', 'retrieve']:
            return SongRetrieveSerializer
        return SongSerializer

    def _change_artists(self, request, remove=False):
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
    def add_artists(self, request, pk=None):
        return self._change_artists(request)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminUser])
    def remove_artists(self, request, pk=None):
        return self._change_artists(request, remove=True)
