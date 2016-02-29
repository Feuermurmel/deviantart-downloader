import sys
from lib import deviantart


def main(user):
	deviantart.download_user_images(user)


main(*sys.argv[1:])
