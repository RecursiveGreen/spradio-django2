from rest_framework.serializers import (IntegerField,
                                        ModelSerializer,
                                        Serializer,
                                        StringRelatedField)

from profiles.models import SongRequest
from radio.models import Song


class JustPlayedSerializer(Serializer):
    song_request = IntegerField()


class MakeRequestSerializer(Serializer):
    song = IntegerField()


class NextSongSerializer(ModelSerializer):
    album = StringRelatedField(many=False)
    artists = StringRelatedField(many=True)
    game = StringRelatedField(many=False)

    class Meta:
        model = Song
        fields = ('id', 'album', 'artists', 'game',
                  'song_type', 'title', 'length', 'path')


class GetRequestSerializer(ModelSerializer):
    song = NextSongSerializer(many=False)

    class Meta:
        model = SongRequest
        fields = ('id', 'song')
