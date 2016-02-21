import sys, os, re, urllib.parse, requests, bs4, unidecode
from lib import util, caches, spiders


def iter_uris(page : spiders.Page):
	for i in page.soup.find_all('a'):
		href = i.get('href')
		
		if href is not None:
			uri, _ = urllib.parse.urldefrag(page.resolve_link(href))
			
			yield urllib.parse.unquote(uri)


def art_page_get_id(page : spiders.Page):
	_, _, path, _, _, _ = urllib.parse.urlparse(page.uri)
	
	return path.rsplit('-', 1)[1]


def art_page_get_title(page : spiders.Page):
	title_container = page.soup.find_all('div', 'dev-title-container')[0]
	title_h1 = title_container.find_all('h1')[0]
	title_a = title_h1.find_all('a')[0]
	
	return title_a.text


def art_get_image_uri(soup : bs4.BeautifulSoup):
	download_button, = soup.find_all('a', 'dev-page-download')
	
	return download_button['href']


def uri_get_ext(uri : str):
	_, _, path, _, _, _ = urllib.parse.urlparse(uri)
	_, ext = os.path.splitext(path)
	
	return ext


def clean_filename(name):
	return re.sub('[^A-Za-z0-9]+', '_', unidecode.unidecode(name))


def download_user_images(user : str):
	spider = spiders.Spider(spiders.Requester(caches.Cache(caches.PersistentDict('cache.db'))))
	domain = '{}.deviantart.com'.format(user)
	
	# def download_image(art_uri, image_uri):
	
	def process_gallery(page : spiders.Page):
		for i in iter_uris(page):
			parts = urllib.parse.urlparse(i)
			
			if parts.netloc == domain:
				if parts.path == '/gallery/':
					arguments = urllib.parse.parse_qs(parts.query)
					
					if '/' in arguments.get('catpath', []):
						if 'sort' not in arguments:
							if 'coffset' not in arguments:
								spider.enqueue(process_gallery, i)
				elif parts.path.startswith('/art/'):
					spider.enqueue(process_art, i)
	
	def process_art(page : spiders.Page):
		dir = os.path.join('download', user)
		id = art_page_get_id(page)
		title = art_page_get_title(page)
		file_name = '{}-{}'.format(id, clean_filename(title))
		
		if not os.path.exists(dir):
			os.makedirs(dir)
		
		if all(i.endswith('~') or os.path.splitext(i)[0] != file_name for i in os.listdir(dir)):
			with requests.session() as session: 
				# Request the page here again, inside a session, which is necessary to get a fresh, working URL for the image.
				response = session.get(page.uri)
				
				# This worked when the spider requested the page so it should also work here.
				assert response.ok
				
				soup = bs4.BeautifulSoup(response.content, 'html.parser')
				image_uri = art_get_image_uri(soup)
				image_ext = uri_get_ext(image_uri)
				image_path = os.path.join(dir, file_name + image_ext)
				temp_path = image_path + '~'
				
				util.log('Downloading image: {}', image_path)
				
				response = session.get(image_uri)
				
				if not response.ok:
					util.log('Error downloading image: {}', response.status_code)
				else:
					content_type = response.headers['content-type']
					
					if not content_type.startswith('image/'):
						util.log('Invalid content type for image: {}', content_type)
					else:
						with open(temp_path, 'wb') as file:
							file.write(response.content)
							os.fsync(file.fileno())
						
						os.rename(temp_path, image_path)
	
	spider.enqueue(process_gallery, urllib.parse.urlunparse(('http', domain, '/gallery/', None, urllib.parse.urlencode(dict(catpath = '/')), None)))
	spider.run()


def main(user):
	download_user_images(user)


main(*sys.argv[1:])
