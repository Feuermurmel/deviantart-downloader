import argparse
from ponydl import util, deviantart


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'user',
        help='Username of the account from which to download ALL THE IMAGES!')

    return parser.parse_args()


def main(user):
    deviantart.download_user_images(user)


def script_main():
    try:
        main(**vars(parse_args()))
    except KeyboardInterrupt:
        util.log('Operation interrupted.')
