from rest_framework.routers import DefaultRouter

from api.views.radio import (AlbumViewSet, ArtistViewSet,
                             GameViewSet, SongViewSet)


router = DefaultRouter()
router.register(r'albums', AlbumViewSet, base_name='album')
router.register(r'artists', ArtistViewSet, base_name='artist')
router.register(r'games', GameViewSet, base_name='game')
router.register(r'songs', SongViewSet, base_name='song')

urlpatterns = router.urls
