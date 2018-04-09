from django.shortcuts import get_object_or_404

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from profiles.models import RadioProfile, Rating, SongRequest
from radio.models import Song
from ..permissions import IsAdminOwnerOrReadOnly
from ..serializers.profiles import (BasicProfileSerializer,
                                    FullProfileSerializer,
                                    FavoriteSongSerializer,
                                    HistorySerializer,
                                    BasicProfileRatingsSerializer)
from ..serializers.radio import BasicSongRetrieveSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOwnerOrReadOnly]
    queryset = RadioProfile.objects.all()
    serializer_class = BasicProfileSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_owner = False

    def get_serializer_class(self):
        '''
        Choose a different serializer based on if the requesting user is an
        admin or is the same person as the profile requested.
        '''
        if self.request.user.is_staff or self.is_owner:
            return FullProfileSerializer
        return BasicProfileSerializer

    def get_object(self):
        '''
        Grab the object as normal, but let us know if the requesting user is
        the owner.
        '''
        obj = get_object_or_404(self.get_queryset(), **self.kwargs)
        if self.request.user.pk == obj.user.pk:
            self.is_owner = True
        else:
            self.is_owner = False
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, permission_classes=[AllowAny])
    def ratings(self, request, pk=None):
        profile = self.get_object()
        ratings = profile.rating_profile.all().order_by('-created_date')

        page = self.paginate_queryset(ratings)
        if page is not None:
            serializer = BasicProfileRatingsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BasicProfileRatingsSerializer(ratings, many=True)
        return Response(serializer.data)

    @action(detail=True, permission_classes=[AllowAny])
    def favorites(self, request, pk=None):
        profile = self.get_object()
        favorites = profile.favorites.all().order_by('sorted_title')

        page = self.paginate_queryset(favorites)
        if page is not None:
            serializer = BasicSongRetrieveSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BasicSongRetrieveSerializer(favorites, many=True)
        return Response(serializer.data)

    def _favorite_change(self, request, remove=False):
        profile = self.get_object()
        serializer = FavoriteSongSerializer(data=request.data)
        if serializer.is_valid():
            song = Song.objects.get(pk=serializer.data['song'])
            if remove:
                profile.favorites.remove(song)
            else:
                profile.favorites.add(song)
            profile.save()
            message = 'Song {} favorites.'.format(('added to',
                                                   'removed from')[remove])
            return Response({'detail': message})
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAdminOwnerOrReadOnly])
    def favorite_add(self, request, pk=None):
        return self._favorite_change(request)

    @action(methods=['post'],
            detail=True,
            permission_classes=[IsAdminOwnerOrReadOnly])
    def favorite_remove(self, request, pk=None):
        return self._favorite_change(request, remove=True)


class HistoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = SongRequest.objects.all()
    serializer_class = HistorySerializer
