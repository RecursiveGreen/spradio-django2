'''
Django management command to import old playlist data. This should only be used
for seeding a newly created database.
'''

import decimal
import json
import os

from django.core.management.base import BaseCommand, CommandError

from core.utils import path_to_iri
from radio.models import Album, Artist, Game, Store, Song

decimal.getcontext().prec = 8


class Command(BaseCommand):
    '''Main "importoldreadio" command class'''
    help = 'Imports the old radio data from an exported playlist'

    def add_arguments(self, parser):
        parser.add_argument('playlist_file', nargs=1)

    def handle(self, *args, **options):
        playlist_file = options['playlist_file'][0]
        if not os.path.isfile(playlist_file):
            raise CommandError('File does not exist')

        with open(playlist_file, 'r', encoding='utf8') as pfile:
            playlist = json.load(pfile, parse_float=decimal.Decimal)

        totals = {
            'albums': 0,
            'artists': 0,
            'games': 0,
            'songs': 0,
            'jingles': 0
        }

        # Fetching albums first
        for album in playlist['albums']:
            Album.objects.create(title=album['title'],
                                 disabled=album['disabled'])
            totals['albums'] += 1

        self.stdout.write('Imported {} albums'.format(str(totals['albums'])))

        # Next up, artists
        for artist in playlist['artists']:
            Artist.objects.create(alias=artist['alias'] or '',
                                  first_name=artist['first_name'] or '',
                                  last_name=artist['last_name'] or '',
                                  disabled=artist['disabled'])
            totals['artists'] += 1

        self.stdout.write('Imported {} artists'.format(str(totals['artists'])))

        # On to games
        for game in playlist['games']:
            Game.objects.create(title=game['title'],
                                disabled=game['disabled'])
            totals['games'] += 1

        self.stdout.write('Imported {} games'.format(str(totals['games'])))

        # Followed by the songs
        for song in playlist['songs']:
            try:
                album = Album.objects.get(title__exact=song['album'])
            except Album.DoesNotExist:
                album = None

            try:
                game = Game.objects.get(title__exact=song['game'])
            except Game.DoesNotExist:
                game = None

            new_song = Song.objects.create(album=album,
                                           game=game,
                                           disabled=song['disabled'],
                                           song_type=song['type'],
                                           title=song['title'])

            for artist in song['artists']:
                new_artist = Artist.objects.get(
                    alias__exact=artist['alias'] or '',
                    first_name__exact=artist['first_name'] or '',
                    last_name__exact=artist['last_name'] or ''
                )
                new_song.artists.add(new_artist)

            new_store = Store.objects.create(
                iri=path_to_iri(song['store']['path']),
                mime_type=song['store']['mime'],
                file_size=song['store']['filesize'],
                length=song['store']['length']
            )
            new_song.stores.add(new_store)
            new_song.current_store = new_store
            new_song.save()
            if song['type'] == 'S':
                totals['songs'] += 1
            else:
                totals['jingles'] += 1

        self.stdout.write(
            'Imported {} requestables ({} songs, {} jingles)'.format(
                str(totals['songs'] + totals['jingles']),
                str(totals['songs']),
                str(totals['jingles'])
            )
        )

        pub = input('Do you want to publish all imported objects as well? '
                    '[Y/N] ')

        if pub in ('Y', 'y'):
            for album in Album.objects.all():
                album.publish()
            for artist in Artist.objects.all():
                artist.publish()
            for game in Game.objects.all():
                game.publish()
            for song in Song.objects.all():
                song.publish()
            self.stdout.write('Published imported objects successfully')
        else:
            self.stdout.write('Skipped publishing songs')
