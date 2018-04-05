from django.urls import path

from rest_framework.routers import DefaultRouter

from api.views.controls import JustPlayed, MakeRequest, NextRequest
from api.views.profiles import HistoryViewSet, ProfileViewSet
from api.views.radio import (AlbumViewSet, ArtistViewSet,
                             GameViewSet, SongViewSet)


class OptionalSlashRouter(DefaultRouter):
    '''
    Custom Router that allows for a trailing slash to be optional in the
    endpoint URI.

    (Thanks to https://stackoverflow.com/questions/46163838/)
    '''
    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'


router = OptionalSlashRouter()

router.register(r'history', HistoryViewSet, base_name='history')
router.register(r'profiles', ProfileViewSet, base_name='profile')

router.register(r'albums', AlbumViewSet, base_name='album')
router.register(r'artists', ArtistViewSet, base_name='artist')
router.register(r'games', GameViewSet, base_name='game')
router.register(r'songs', SongViewSet, base_name='song')

urlpatterns = [
    path('next/', NextRequest.as_view()),
    path('played/', JustPlayed.as_view()),
    path('request/', MakeRequest.as_view()),
]

urlpatterns += router.urls
