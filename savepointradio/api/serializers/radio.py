from rest_framework.serializers import (DecimalField, IntegerField, ListField,
                                        ModelSerializer, Serializer,
                                        SerializerMethodField,
                                        StringRelatedField)

from core.utils import iri_to_path
from radio.models import Album, Artist, Game, Song, Store


class AlbumSerializer(ModelSerializer):
    '''A base serializer for an album model.'''
    class Meta:
        model = Album
        fields = ('id', 'title')


class ArtistSerializer(ModelSerializer):
    '''A base serializer for an artist model.'''
    class Meta:
        model = Artist
        fields = ('id', 'alias', 'first_name', 'last_name')


class ArtistFullnameSerializer(ModelSerializer):
    '''
    A base serializer for an artist model, but combining all name
    attributes into one field.
    '''
    class Meta:
        model = Artist
        fields = ('id', 'full_name')


class GameSerializer(ModelSerializer):
    '''A base serializer for a game model.'''
    class Meta:
        model = Game
        fields = ('id', 'title')


class StoreSerializer(ModelSerializer):
    '''A base serializer for a data store model.'''
    active = SerializerMethodField()

    class Meta:
        model = Store
        fields = ('id', 'iri', 'file_size', 'length', 'mime_type')

    def get_active(self, obj):
        '''Checks to see if this store is active for a song.'''
        if obj.active_for:
            return True
        return False


class SongSerializer(ModelSerializer):
    '''A base serializer for a song model.'''
    length = DecimalField(
        max_digits=10,
        decimal_places=2,
        source='active_store.length'
    )

    class Meta:
        model = Song
        fields = ('id', 'album', 'artists', 'published_date', 'game',
                  'num_played', 'last_played', 'length', 'next_play',
                  'song_type', 'title', 'average_rating', 'is_requestable')


class SongMinimalSerializer(ModelSerializer):
    '''Minimal song information, usually appended to favorites/ratings.'''
    album = AlbumSerializer()
    artists = ArtistFullnameSerializer(many=True)
    game = GameSerializer()

    class Meta:
        model = Song
        fields = ('id', 'album', 'artists', 'game', 'title')


class SongListSerializer(ModelSerializer):
    '''Song information used in large listings.'''
    album = AlbumSerializer()
    artists = ArtistFullnameSerializer(many=True)
    game = GameSerializer()
    length = DecimalField(
        max_digits=10,
        decimal_places=2,
        source='active_store.length'
    )

    class Meta:
        model = Song
        fields = ('id', 'album', 'artists', 'game', 'title', 'average_rating',
                  'length', 'is_requestable')


class SongRetrieveSerializer(SongSerializer):
    '''
    An almost complete listing of a song's information, based on a single
    object retrieval.
    '''
    album = AlbumSerializer()
    artists = ArtistSerializer(many=True)
    game = GameSerializer()


class RadioSongSerializer(ModelSerializer):
    '''
    A song serializer that is specific to the radio DJ and the underlying
    audio manipulation application.
    '''
    album = StringRelatedField()
    artists = StringRelatedField(many=True)
    game = StringRelatedField()
    length = DecimalField(
        max_digits=10,
        decimal_places=2,
        source='active_store.length'
    )
    path = SerializerMethodField()

    class Meta:
        model = Song
        fields = ('album', 'artists', 'game', 'song_type', 'title', 'length',
                  'path')

    def get_path(self, obj):
        '''Converts the IRI into a filesystem path.'''
        iri = str(obj.active_store.iri)
        if iri.startswith('file://'):
            return iri_to_path(iri)
        return iri


class SongArtistsListSerializer(Serializer):
    '''
    A serializer for adding or removing artists from a song based on
    the song's id number.
    '''
    artists = ListField(child=IntegerField(), min_length=1, max_length=10)
