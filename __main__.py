import argparse
from ponydl import deviantart


def parse_args():
	parser = argparse.ArgumentParser()
	
	parser.add_argument('user', help = 'Username of the account from which to download ALL THE IMAGES!')
	
	return parser.parse_args()


def main(user):
	deviantart.download_user_images(user)


main(**vars(parse_args()))
