from decimal import *
import os
import sqlite3

from django.core.management.base import BaseCommand, CommandError

from radio.models import Album, Artist, Game, Song

getcontext().prec = 8


def adapt_decimal(d):
    return str(d)


def convert_decimal(s):
    return Decimal(s.decode('utf8'))


sqlite3.register_adapter(Decimal, adapt_decimal)
sqlite3.register_converter("decimal", convert_decimal)


class Command(BaseCommand):
    help = 'Imports the old radio data from the original sqlite3 database'

    def add_arguments(self, parser):
        parser.add_argument('sqlite3_db_file', nargs=1)

    def handle(self, *args, **options):
        if not os.path.isfile(options['sqlite3_db_file'][0]):
            raise CommandError('File does not exist')
        else:
            total_albums = 0
            total_artists = 0
            total_games = 0
            total_songs = 0
            total_jingles = 0

            detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            con = sqlite3.connect(options['sqlite3_db_file'][0],
                                  detect_types=detect_types)
            cur = con.cursor()

            # Fetching albums first
            for album in con.execute('SELECT title, enabled FROM albums'):
                album_disabled = not bool(album[1])
                Album.objects.create(title=album[0], disabled=album_disabled)
                total_albums += 1

            self.stdout.write('Imported {} albums'.format(str(total_albums)))

            # Next up, artists
            cur.execute('''SELECT
                            artists_id,
                            alias,
                            firstname,
                            lastname,
                            enabled
                        FROM artists''')
            artists = cur.fetchall()

            for artist in artists:
                artist_disabled = not bool(artist[4])
                Artist.objects.create(alias=artist[1] or '',
                                      first_name=artist[2] or '',
                                      last_name=artist[3] or '',
                                      disabled=artist_disabled)
                total_artists += 1

            self.stdout.write('Imported {} artists'.format(str(total_artists)))

            # On to games
            for game in con.execute('SELECT title, enabled FROM games'):
                game_disabled = not bool(game[1])
                Game.objects.create(title=game[0], disabled=game_disabled)
                total_games += 1

            self.stdout.write('Imported {} games'.format(str(total_games)))

            # Followed by the songs
            cur.execute('''SELECT
                            songs.songs_id AS id,
                            games.title AS game,
                            albums.title AS album,
                            songs.enabled AS enabled,
                            songs.type AS type,
                            songs.title AS title,
                            songs.length AS length,
                            songs.path AS path
                        FROM songs
                        LEFT JOIN games
                            ON (songs.game = games.games_id)
                        LEFT JOIN albums
                            ON (songs.album = albums.albums_id)''')
            songs = cur.fetchall()

            for song in songs:
                try:
                    album = Album.objects.get(title__exact=song[2])
                except Album.DoesNotExist:
                    album = None

                try:
                    game = Game.objects.get(title__exact=song[1])
                except Game.DoesNotExist:
                    game = None

                song_disabled = not bool(song[3])
                new_song = Song.objects.create(album=album,
                                               game=game,
                                               disabled=song_disabled,
                                               song_type=song[4],
                                               title=song[5],
                                               length=song[6],
                                               path=song[7])
                if song[4] == 'S':
                    total_songs += 1
                else:
                    total_jingles += 1

                cur.execute('''SELECT
                                ifnull(alias, "") AS alias,
                                ifnull(firstname, "") AS firstname,
                                ifnull(lastname, "") AS lastname
                            FROM artists
                            WHERE artists_id
                            IN (SELECT artists_artists_id
                                FROM songs_have_artists
                                WHERE songs_songs_id = ?)''', [song[0]])
                old_artists = cur.fetchall()
                for old_artist in old_artists:
                    new_artist = Artist.objects.get(alias__exact=old_artist[0],
                                                    first_name__exact=old_artist[1],
                                                    last_name__exact=old_artist[2])
                    new_song.artists.add(new_artist)

            self.stdout.write(
                'Imported {} requestables ({} songs, {} jingles)'.format(
                    str(total_songs + total_jingles),
                    str(total_songs),
                    str(total_jingles)
                )
            )

            pub = input('Do you want to publish all imported objects as well? '
                        '[Y/N] ')

            if pub == 'Y' or pub == 'y':
                for al in Album.objects.all():
                    al.publish()
                for ar in Artist.objects.all():
                    ar.publish()
                for g in Game.objects.all():
                    g.publish()
                for s in Song.objects.all():
                    s.publish()
                self.stdout.write('Published imported objects successfully')
            else:
                self.stdout.write('Skipped publishing songs')
