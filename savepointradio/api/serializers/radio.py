from rest_framework.serializers import (IntegerField, ListField,
                                        ModelSerializer, Serializer,
                                        StringRelatedField)

from radio.models import Album, Artist, Game, Song


class AlbumSerializer(ModelSerializer):
    class Meta:
        model = Album
        fields = ('id', 'title')


class ArtistSerializer(ModelSerializer):
    class Meta:
        model = Artist
        fields = ('id', 'alias', 'first_name', 'last_name')


class ArtistFullnameSerializer(ModelSerializer):
    class Meta:
        model = Artist
        fields = ('id', 'full_name')


class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'title')


class BasicSongSerializer(ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'album', 'artists', 'game', 'title', 'average_rating',
                  'is_requestable')


class FullSongSerializer(ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'album', 'artists', 'published_date', 'game',
                  'num_played', 'last_played', 'length', 'song_type', 'title',
                  'average_rating', 'is_requestable')


class BasicSongRetrieveSerializer(BasicSongSerializer):
    album = AlbumSerializer()
    artists = ArtistFullnameSerializer(many=True)
    game = GameSerializer()


class FullSongRetrieveSerializer(FullSongSerializer):
    album = AlbumSerializer()
    artists = ArtistSerializer(many=True)
    game = GameSerializer()


class RadioSongSerializer(ModelSerializer):
    album = StringRelatedField()
    artists = StringRelatedField(many=True)
    game = StringRelatedField()

    class Meta:
        model = Song
        fields = ('album', 'artists', 'game', 'song_type', 'title', 'length',
                  'path')


class SongArtistsListSerializer(Serializer):
    artists = ListField(child=IntegerField(), min_length=1, max_length=10)
