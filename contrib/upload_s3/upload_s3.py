'''
upload_s3.py

This is the helper script that uploads songs from an exported playlist into
an Amazon S3 instance (or other implementations, like DigialOcean Spaces).
'''

import argparse
import json
import logging
import os
import sys
import threading
import traceback
from unicodedata import normalize

from decouple import config
import boto3

# If these four are not defined, then boto3 will look for defaults in the
# ~/.aws configurations
S3_REGION = config('S3_REGION', default=None)
S3_ENDPOINT = config('S3_ENDPOINT', default=None)
S3_ACCESS_KEY = config('S3_ACCESS_KEY', default=None)
S3_SECRET_KEY = config('S3_SECRET_KEY', default=None)

# This has to be defined regardless.
S3_BUCKET = config('S3_BUCKET')

# Radio name for metadata
RADIO_NAME = config('RADIO_NAME', default='Save Point Radio')

logging.basicConfig(
        handlers=[logging.FileHandler('./s3_uploads.log', encoding='utf8')],
        level=logging.INFO,
        format=('[%(asctime)s] [%(levelname)s]'
                ' [%(name)s.%(funcName)s] === %(message)s'),
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
LOGGER = logging.getLogger('upload_s3')


class Progress(object):
    '''
    A callback class for the Amazon S3 upload to detect how far along in an
    upload we are.
    '''
    def __init__(self, filepath):
        self._filepath = filepath
        self._filename = os.path.basename(filepath)
        self._size = float(os.path.getsize(filepath))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage
                )
            )
            sys.stdout.flush()


def asciify(text):
    '''
    Converts a unicode string to pure ascii.
    '''
    normal = normalize('NFKC', text)
    return normal.encode('ascii', 'backslashreplace').decode('ascii')


def get_fullname(artist):
    '''
    String representing the artist's full name including an alias, if
    available.
    '''
    if artist['alias']:
        if artist['first_name'] or artist['last_name']:
            return '{} "{}" {}'.format(artist['first_name'],
                                       artist['alias'],
                                       artist['last_name'])
        return artist['alias']
    return '{} {}'.format(artist['first_name'], artist['last_name'])


def beautify_artists(artists):
    '''
    Turns a list of one or more artists into a proper English listing.
    '''
    fullnames = [get_fullname(artist) for artist in artists]
    output = ', '
    if len(fullnames) == 2:
        output = ' & '
    return output.join(fullnames)


def import_playlist(playlist_file):
    '''
    Imports a playlist from a JSON file, uploads the files to an S3[-like]
    instance, and exports a new JSON file with the updated paths.
    '''
    if not os.path.isfile(playlist_file):
        raise FileNotFoundError

    with open(playlist_file, 'r', encoding='utf8') as pfile:
        playlist = json.load(pfile)

    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    )

    totals = {'success': 0, 'fail': 0}

    for song in playlist['songs']:
        old_path = song['store']['path']

        if song['type'] == 'S':
            prefix = 'songs'
            metadata = {
                'album': asciify(song['album']),
                'artists': asciify(beautify_artists(song['artists'])),
                'game': asciify(song['game']),
                'title': asciify(song['title']),
                'length': str(song['store']['length']),
                'original-path': asciify(old_path)
            }
        else:
            prefix = 'jingles'
            metadata = {
                'artists': asciify(RADIO_NAME),
                'title': asciify(song['title']),
                'length': str(song['store']['length']),
                'original-path': asciify(old_path)
            }
        file_hash = song['store']['filehash']
        ext = os.path.splitext(old_path)[1]
        new_path = '{}/{}{}'.format(prefix, file_hash, ext)

        LOGGER.info('Begin upload of: %s', old_path)

        try:
            client.upload_file(
                old_path,
                S3_BUCKET,
                new_path,
                ExtraArgs={
                    'Metadata': metadata,
                    'ContentType': song['store']['mime']
                },
                Callback=Progress(old_path)
            )
        except Exception:
            LOGGER.error(
                'Upload failed for: %s -- %s',
                old_path,
                traceback.print_exc()
            )
            totals['fail'] += 1
        else:
            song['store']['path'] = 's3://{}/{}'.format(S3_BUCKET, new_path)
            LOGGER.info(
                'Successful upload of: %s to %s',
                old_path,
                song['store']['path']
            )
            totals['success'] += 1

        sys.stdout.write("\r\n")
        sys.stdout.flush()

    result_message = 'Uploads complete -- {} successful, {} failures'.format(
        totals['success'],
        totals['fail']
    )
    print(result_message)
    LOGGER.info(result_message)

    return playlist


def main():
    '''Main loop of the program'''

    description = 'Uploads song files to an Amazon S3 (or similar) instance.'

    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(dest='command')

    parser_playlist = subparsers.add_parser(
        'playlist',
        help='Import playlist song data.'
    )
    parser_playlist.add_argument(
        'filepath',
        help='Path to the playlist file.',
        nargs=1
    )

    if len(sys.argv) == 1:
        sys.stderr.write('Error: please specify a command\n\n')
        parser.print_help(sys.stderr)
        sys.exit(1)

    results = None

    args = parser.parse_args()

    if args.command == 'playlist':
        results = import_playlist(args.filepath[0])

    if results:
        LOGGER.info('Exporting new playlist file to \'playlist_s3.json\'')
        with open('playlist_s3.json', 'w', encoding='utf8') as file:
            json.dump(
                results,
                file,
                ensure_ascii=False,
                sort_keys=True,
                indent=4
            )
    LOGGER.info('Program finished. Exiting.')


if __name__ == '__main__':
    main()
