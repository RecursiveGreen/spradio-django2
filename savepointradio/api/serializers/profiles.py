from django.contrib.auth import get_user_model

from rest_framework.serializers import ModelSerializer

from profiles.models import (RadioProfile, SongRequest)


User = get_user_model()


class HistorySerializer(ModelSerializer):
    class Meta:
        model = SongRequest
        fields = ('created_date', 'played_at', 'profile', 'song')


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
