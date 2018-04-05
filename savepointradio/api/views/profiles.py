from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from profiles.models import RadioProfile, Rating, SongRequest
from ..permissions import IsAdminOwnerOrReadOnly
from ..serializers.profiles import (BasicProfileSerializer,
                                    FullProfileSerializer,
                                    HistorySerializer)


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
