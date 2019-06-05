'''
export_playlist.py

This is the helper script that exports old playlist databases to be reimported
by the new database later.
'''

import argparse
from decimal import Decimal, getcontext
import json
import mimetypes
import os
import sqlite3
import sys
import unicodedata

import magic


def scrub(text):
    '''
    Forcing a Unicode NFC normalization to remove combining marks that mess
    with certain Python functions.
    '''
    if text:
        return unicodedata.normalize('NFC', text)
    return None


def detect_mime(path):
    '''
    Guess a file's mimetype from it's magic number. If inconclusive, then
    guess based on it's file extension.
    '''
    mimetype = magic.from_file(path, mime=True)
    if mimetype == 'application/octet-stream':
        return mimetypes.guess_type(path, strict=True)[0]
    return mimetype


def adapt_decimal(number):
    '''Sqlite3 adapter for Decimal types'''
    return str(number)


def convert_decimal(text):
    '''Sqlite3 converter for Decimal types'''
    return float(text.decode('utf8'))


def import_sqlite3(db_file):
    '''
    Imports a playlist from an SQLite3 database file and exports to a
    JSON file.
    '''
    totals = {
        'albums': 0,
        'artists': 0,
        'games': 0,
        'songs': 0,
        'jingles': 0
    }

    if not os.path.isfile(db_file):
        raise FileNotFoundError

    detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    con = sqlite3.connect(db_file, detect_types=detect_types)
    cur = con.cursor()

    # Fetching albums first
    albums = list()
    for album in con.execute('SELECT title, enabled FROM albums'):
        albums.append({
            'title': scrub(album[0]),
            'disabled': not bool(album[1])
        })
        totals['albums'] += 1
    print('Exported {} albums'.format(str(totals['albums'])))

    # Next up, artists
    artists = list()
    artist_query = 'SELECT alias, firstname, lastname, enabled FROM artists'
    for artist in con.execute(artist_query):
        artists.append({
            'alias': scrub(artist[0]) or '',
            'first_name': scrub(artist[1]) or '',
            'last_name': scrub(artist[2]) or '',
            'disabled': not bool(artist[3])
        })
        totals['artists'] += 1
    print('Exported {} artists'.format(str(totals['artists'])))

    # On to games
    games = list()
    for game in con.execute('SELECT title, enabled FROM games'):
        games.append({
            'title': scrub(game[0]),
            'disabled': not bool(game[1])
        })
        totals['games'] += 1
    print('Exported {} games'.format(str(totals['games'])))

    # Now the songs
    songs = list()
    songs_query = '''SELECT
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
                        ON (songs.album = albums.albums_id)'''
    cur.execute(songs_query)
    old_songs = cur.fetchall()
    for song in old_songs:
        # Deal with the list of artists
        song_artists = list()
        song_artist_query = '''SELECT
                                    ifnull(alias, "") AS alias,
                                    ifnull(firstname, "") AS firstname,
                                    ifnull(lastname, "") AS lastname
                                FROM artists
                                WHERE artists_id
                                IN (SELECT artists_artists_id
                                    FROM songs_have_artists
                                    WHERE songs_songs_id = ?)'''
        cur.execute(song_artist_query, [song[0]])
        song_artist_results = cur.fetchall()
        for artist in song_artist_results:
            song_artists.append({
                'alias': scrub(artist[0]),
                'first_name': scrub(artist[1]),
                'last_name': scrub(artist[2])
            })
        store = {'path': scrub(song[7]),
                 'mime': detect_mime(scrub(song[7])),
                 'filesize': os.stat(scrub(song[7])).st_size,
                 'length': song[6]}
        songs.append({'album': scrub(song[2]),
                      'artists': song_artists,
                      'game': scrub(song[1]),
                      'disabled': not bool(song[3]),
                      'type': song[4],
                      'title': scrub(song[5]),
                      'store': store})
        if song[4] == 'S':
            totals['songs'] += 1
        else:
            totals['jingles'] += 1
    print('Exported {} requestables ({} songs, {} jingles)'.format(
        str(totals['songs'] + totals['jingles']),
        str(totals['songs']),
        str(totals['jingles'])
    ))

    return {'albums': albums,
            'artists': artists,
            'games': games,
            'songs': songs}


def main():
    '''Main loop of the program'''
    getcontext().prec = 8

    sqlite3.register_adapter(Decimal, adapt_decimal)
    sqlite3.register_converter("decimal", convert_decimal)

    description = 'Exports old playlist to a file for reimporting later.'

    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(dest='command')

    parser_sqlite3 = subparsers.add_parser(
        'sqlite3',
        help='Imports old Sqlite3 database.'
    )
    parser_sqlite3.add_argument(
        'db_file',
        help='Path to the sqlite3 database file.',
        nargs=1
    )

    if len(sys.argv) == 1:
        sys.stderr.write('Error: please specify a command\n\n')
        parser.print_help(sys.stderr)
        sys.exit(1)

    results = None

    args = parser.parse_args()

    if args.command == 'sqlite3':
        results = import_sqlite3(args.db_file[0])

    if results:
        with open('playlist.json', 'w', encoding='utf8') as file:
            json.dump(results,
                      file,
                      ensure_ascii=False,
                      sort_keys=True,
                      indent=4)


if __name__ == '__main__':
    main()
