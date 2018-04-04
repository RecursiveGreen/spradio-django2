from rest_framework import serializers

from radio.models import Album, Artist, Game, Song


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ('id', 'title')


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ('id', 'alias', 'first_name', 'last_name')


class ArtistFullnameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ('id', 'full_name')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'title')


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'album', 'artists', 'published_date', 'game',
                  'num_played', 'last_played', 'length', 'song_type', 'title')


class SongRetrieveSerializer(SongSerializer):
    artists = ArtistFullnameSerializer(many=True)


class SongArtistsListSerializer(serializers.Serializer):
    artists = serializers.ListField(child=serializers.IntegerField(),
                                    min_length=1,
                                    max_length=10)
