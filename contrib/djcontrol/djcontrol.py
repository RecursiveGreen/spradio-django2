'''
djcontrol.py

This is the helper script that glues the webapi/database to the liquidsoap
application. We make RESTful requests here to get the next song and to report
when a song has been played.
'''

import argparse
import json

import requests


DJ_TOKEN = 'place_generated_token_here'

API_URL = 'https://savepointradio.net/api/'

RADIO_NAME = 'Save Point Radio'

HEADERS = {
    'Content-Type': 'application/json; charset=utf-8',
    'Authorization': 'Token {}'.format(DJ_TOKEN)
}

ANNOTATE = 'annotate:req_id="{}",type="{}",artist="{}",title="{}",game="{}":{}'


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


description = 'Lets the DJ control the radio.'

parser = argparse.ArgumentParser(description=description)
subparsers = parser.add_subparsers(dest='command')

parser_next = subparsers.add_parser('next',
                                    help='Gets the next song from the radio.')
parser_played = subparsers.add_parser('played',
                                      help='Tells the radio which song just played.')
parser_played.add_argument('request',
                           help='Song request ID number.',
                           nargs=1,
                           type=int)

args = parser.parse_args()

if args.command == 'next':
    try:
        r = requests.get(API_URL + 'next/',
                         headers=HEADERS,
                         timeout=5)
        r.encoding = 'utf-8'
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print('Http Error: {}'.format(errh))
    except requests.exceptions.ConnectionError as errc:
        print('Error Connecting: {}'.format(errc))
    except requests.exceptions.Timeout as errt:
        print('Timeout Error: {}'.format(errt))
    except requests.exceptions.RequestException as err:
        print('Error: {}'.format(err))
    else:
        req = json.loads(r.text)
        song = req['song']
        if song['song_type'] == 'J':
            artist = RADIO_NAME
            title = 'Jingle'
            game = RADIO_NAME
        else:
            artist = beautify_artists(song['artists'])
            title = clean_quotes(song['title'])
            game = clean_quotes(song['game'])
        print(ANNOTATE.format(req['id'],
                              song['song_type'],
                              artist,
                              title,
                              game,
                              song['path']))
elif args.command == 'played':
    try:
        req_played = json.dumps({'song_request': args.request[0]})
        r = requests.post(API_URL + 'played/',
                          headers=HEADERS,
                          data=req_played,
                          timeout=5)
        r.encoding = 'utf-8'
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print('Http Error: {}'.format(errh))
        print(r.text)
    except requests.exceptions.ConnectionError as errc:
        print('Error Connecting: {}'.format(errc))
    except requests.exceptions.Timeout as errt:
        print('Timeout Error: {}'.format(errt))
    except requests.exceptions.RequestException as err:
        print('Error: {}'.format(err))
