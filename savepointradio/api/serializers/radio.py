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


class SongCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'album', 'artists', 'published_date', 'game',
                  'num_played', 'last_played', 'length', 'song_type', 'title')

    def create(self, validated_data):
        artists_data = validated_data.pop('artists')
        song = Song.objects.create(**validated_data)
        for artist_data in artists_data:
            song.artists.add(artist_data)
        song.save()
        return song


class SongSerializer(SongCreateSerializer):
    artists = ArtistFullnameSerializer(many=True)
