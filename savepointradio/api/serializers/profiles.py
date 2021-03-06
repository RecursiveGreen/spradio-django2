from django.contrib.auth import get_user_model

from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        Serializer)

from profiles.models import RadioProfile, SongRequest, Rating
from .radio import SongMinimalSerializer


User = get_user_model()


class BasicUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'is_staff')


class FullUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'is_staff', 'is_active', 'last_login')


class BasicProfileSerializer(ModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = RadioProfile
        fields = ('id', 'user')


class FullProfileSerializer(BasicProfileSerializer):
    user = FullUserSerializer()


class FavoriteSongSerializer(Serializer):
    song = IntegerField()


class RateSongSerializer(Serializer):
    value = IntegerField(min_value=0, max_value=5, required=False)


class HistorySerializer(ModelSerializer):
    profile = BasicProfileSerializer()
    song = SongMinimalSerializer()

    class Meta:
        model = SongRequest
        fields = ('created_date', 'played_at', 'profile', 'song')


class BasicProfileRatingsSerializer(ModelSerializer):
    song = SongMinimalSerializer()

    class Meta:
        model = Rating
        fields = ('created_date', 'song', 'value')


class BasicSongRatingsSerializer(ModelSerializer):
    profile = BasicProfileSerializer()

    class Meta:
        model = Rating
        fields = ('created_date', 'profile', 'value')
