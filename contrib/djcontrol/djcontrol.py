'''
djcontrol.py

This is the helper script that glues the webapi/database to the liquidsoap
application. We make RESTful requests here to get the next song and to report
when a song has been played.
'''

import argparse
import json
import logging
from logging.handlers import RotatingFileHandler

from decouple import config
import requests


DJ_TOKEN = config('DJ_TOKEN')

API_URL = config('API_URL')  # With trailing slash

RADIO_NAME = config('RADIO_NAME')

HEADERS = {
    'Content-Type': 'application/json; charset=utf-8',
    'Authorization': 'Token {}'.format(DJ_TOKEN)
}

ANNOTATE = (
    'annotate:req_id="{}",'
    'type="{}",'
    'artist="{}",'
    'title="{}",'
    'game="{}",'
    'replay_gain="{}":{}'
)

logging.basicConfig(
        handlers=[
            RotatingFileHandler(
                './song_requests.log',
                maxBytes=1000000,
                backupCount=5,
                encoding='utf8'
            )
        ],
        level=logging.INFO,
        format=('[%(asctime)s] [%(levelname)s]'
                ' [%(name)s.%(funcName)s] === %(message)s'),
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
LOGGER = logging.getLogger('djcontrol')


def clean_quotes(unclean_string):
    '''
    Escapes quotes for use in the Liquidsoap parser.
    '''
    return unclean_string.replace('"', '\\"')


def beautify_artists(artists):
    '''
    Turns a list of one or more artists into a proper English listing.
    '''
    output = ', '
    if len(artists) == 2:
        output = ' & '
    return clean_quotes(output.join(artists))


def next_request():
    '''
    Sends an HTTP[S] request to the radio web service to retrieve the next
    requested song.
    '''
    LOGGER.debug('Received command to get next song request.')
    try:
        resp = requests.get(API_URL + 'next/', headers=HEADERS, timeout=5)
        resp.encoding = 'utf-8'
        resp.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        LOGGER.error('Http Error: %s', errh)
    except requests.exceptions.ConnectionError as errc:
        LOGGER.error('Error Connecting: %s', errc)
    except requests.exceptions.Timeout as errt:
        LOGGER.error('Timeout Error: %s', errt)
    except requests.exceptions.RequestException as err:
        LOGGER.error('Error: %s', err)
    else:
        LOGGER.debug('Received JSON response: %s', resp.text)
        song_request = json.loads(resp.text)
        song = song_request['song']
        if song['song_type'] == 'J':
            artist = RADIO_NAME
            title = 'Jingle'
            game = RADIO_NAME
        else:
            artist = beautify_artists(song['artists'])
            title = clean_quotes(song['title'])
            game = clean_quotes(song['game'])
        LOGGER.info(
            'ID: %s, Artist[s]: %s, Title: %s, Game: %s, Gain: %s, Path: %s',
            song_request['id'],
            artist,
            title,
            game,
            song['replaygain'],
            song['path']
        )
        annotate_string = ANNOTATE.format(
            song_request['id'],
            song['song_type'],
            artist,
            title,
            game,
            song['replaygain'],
            song['path']
        )
        LOGGER.debug(annotate_string)
        print(annotate_string)


def just_played(request_id):
    '''
    Sends an HTTP[S] request to the radio web service to let it know that a
    song has been played.
    '''
    LOGGER.debug('Received command to report a song was just played.')
    try:
        request_played = json.dumps({'song_request': request_id})
        resp = requests.post(
            API_URL + 'played/',
            headers=HEADERS,
            data=request_played,
            timeout=5
        )
        resp.encoding = 'utf-8'
        resp.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        LOGGER.error('Http Error: %s', errh)
    except requests.exceptions.ConnectionError as errc:
        LOGGER.error('Error Connecting: %s', errc)
    except requests.exceptions.Timeout as errt:
        LOGGER.error('Timeout Error: %s', errt)
    except requests.exceptions.RequestException as err:
        LOGGER.error('Error: %s', err)
    else:
        LOGGER.info('Req_ID: %s', request_id)


def main():
    '''Main loop of the program'''
    description = 'Lets the DJ control the radio.'

    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(dest='command')

    parser_next = subparsers.add_parser(
        'next',
        help='Gets the next song from the radio.'
    )

    parser_played = subparsers.add_parser(
        'played',
        help='Tells the radio which song just played.'
    )
    parser_played.add_argument(
        'request',
        help='Song request ID number.',
        nargs=1,
        type=int
    )

    args = parser.parse_args()

    if args.command == 'next':
        next_request()
    elif args.command == 'played':
        just_played(args.request[0])


if __name__ == '__main__':
    main()
