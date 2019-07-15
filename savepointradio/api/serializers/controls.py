from rest_framework.serializers import (IntegerField,
                                        ModelSerializer,
                                        Serializer)

from profiles.models import SongRequest
from .radio import RadioSongSerializer


class JustPlayedSerializer(Serializer):
    song_request = IntegerField()


class MakeRequestSerializer(Serializer):
    song = IntegerField()


class GetRequestSerializer(ModelSerializer):
    song = RadioSongSerializer()

    class Meta:
        model = SongRequest
        fields = ('id', 'song')
