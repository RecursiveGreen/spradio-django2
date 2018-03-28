from rest_framework import viewsets

from radio.models import Album, Artist, Game, Song
from ..permissions import IsAdminOrReadOnly
from ..serializers.radio import (AlbumSerializer, ArtistSerializer,
                                 GameSerializer, SongSerializer)


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
