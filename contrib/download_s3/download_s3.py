'''
download_s3.py

This is the helper script that downloads songs from an Amazon S3 instance
(or other implementations, like DigialOcean Spaces). Currently used as a
workaround for a pipe-leaking issue with the "aws-cli" client.
'''

import argparse
import logging
import sys
import traceback

from decouple import config
import boto3

# If these four are not defined, then boto3 will look for defaults in the
# ~/.aws configurations
S3_REGION = config('S3_REGION', default=None)
S3_ENDPOINT = config('S3_ENDPOINT', default=None)
S3_ACCESS_KEY = config('S3_ACCESS_KEY', default=None)
S3_SECRET_KEY = config('S3_SECRET_KEY', default=None)

# Radio name for metadata
RADIO_NAME = config('RADIO_NAME', default='Save Point Radio')

logging.basicConfig(
        handlers=[logging.FileHandler('./s3_downloads.log', encoding='utf8')],
        level=logging.INFO,
        format=('[%(asctime)s] [%(levelname)s]'
                ' [%(name)s.%(funcName)s] === %(message)s'),
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
LOGGER = logging.getLogger('download_s3')


def download_file(s3path, filepath):
    '''
    Downloads a file from an S3 instance and saves it to a specified path.
    '''

    obj_parts = s3path[5:].split('/')
    obj_bucket = obj_parts[0]
    obj_key = '/'.join(obj_parts[1:])

    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    )

    try:
        client.download_file(obj_bucket, obj_key, filepath)
    except Exception:
        LOGGER.error(
            'Download failed for: %s -- %s',
            s3path,
            traceback.print_exc()
        )
        result = 1
    else:
        LOGGER.info(
            'Successful download of: %s to %s',
            s3path,
            filepath
        )
        result = 0

    return result


def main():
    '''Main loop of the program'''

    description = 'Downloads songs from an Amazon S3 (or similar) instance.'

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        's3path',
        help='Path to the S3 object',
        nargs=1
    )

    parser.add_argument(
        'filepath',
        help='Path to place the downloaded file',
        nargs=1
    )

    if len(sys.argv) == 1:
        sys.stderr.write('Error: please specify a command\n\n')
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.s3path and args.filepath:
        result = download_file(args.s3path[0], args.filepath[0])

    LOGGER.info('Program finished. Exiting.')
    sys.exit(result)


if __name__ == '__main__':
    main()
