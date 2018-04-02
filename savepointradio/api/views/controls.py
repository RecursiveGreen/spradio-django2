from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import get_setting
from profiles.exceptions import MakeRequestError
from profiles.models import RadioProfile, SongRequest
from radio.models import Song
from ..permissions import IsDJ
from ..serializers.controls import (JustPlayedSerializer,
                                    MakeRequestSerializer,
                                    GetRequestSerializer)


User = get_user_model()


class JustPlayed(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDJ]

    def post(self, request, format=None):
        serializer = JustPlayedSerializer(data=request.data)
        if serializer.is_valid():
            request_pk = serializer.data['song_request']
            song_request = SongRequest.objects.get(pk=request_pk)
            song_request.played_at = timezone.now()
            song_request.save(update_fields=['played_at'])

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NextRequest(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDJ]
    queryset = SongRequest.objects.all()
    serializer = GetRequestSerializer

    def retrieve(self, request):
        dj_profile = RadioProfile.objects.get(user__is_dj=True)

        limit = get_setting('songs_per_jingle')
        played_songs = SongRequest.music.get_played_requests(limit)
        if [j for j in played_songs if j.song.is_jingle]:
            if not SongRequest.music.unplayed().exists():
                random_song = Song.music.get_random_requestable_song()
                next_play = SongRequest.objects.create(profile=dj_profile,
                                                       song=random_song)
            else:
                next_play = SongRequest.music.next_request()
        else:
            random_jingle = Song.music.get_random_jingle()
            next_play = SongRequest.objects.create(profile=dj_profile,
                                                   song=random_jingle)

        next_play.queued_at = timezone.now()
        next_play.save(update_fields=['queued_at'])

        serializer = GetRequestSerializer(next_play, many=False)
        return Response(serializer.data)


class MakeRequest(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = MakeRequestSerializer(data=request.data)
        if serializer.is_valid():
            profile = RadioProfile.objects.get(user=request.user)
            try:
                profile.make_request(serializer.data['song'])
            except MakeRequestError as e:
                return Response({'detail': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
