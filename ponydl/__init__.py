import argparse
from ponydl import util, deviantart


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-o',
        '--output-dir',
        help='Path to the directory into which to download the images. '
             'Defaults to a directory with the user\'s name in the current '
             'directory.')

    parser.add_argument(
        'user',
        help='Username of the account from which to download ALL THE IMAGES!')

    return parser.parse_args()


def main(user, output_dir):
    if output_dir is None:
        output_dir = user

    deviantart.download_user_images(user, output_dir)


def script_main():
    try:
        main(**vars(parse_args()))
    except KeyboardInterrupt:
        util.log('Operation interrupted.')
