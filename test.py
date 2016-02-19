import urllib.parse, bs4, requests


def iter_uris(soup, base_uri):
	for i in soup.find_all('a'):
		href = i.get('href')
		
		if href is not None:
			uri, _ = urllib.parse.urldefrag(urllib.parse.urljoin(base_uri, href))
			
			yield uri


def walk_galleries():
	prefix = 'http://joycall3.deviantart.com/gallery/'
	found_uris = set()
	
	def walk(uri):
		response = requests.get(uri)
		soup = bs4.BeautifulSoup(response.text, 'html.parser')
		
		for i in iter_uris(soup, uri):
			if i.startswith(prefix) and i not in found_uris:
				found_uris.add(i)
				walk(i)
	
	walk(prefix)
	
	return found_uris


def main():
	# url = 'http://joycall3.deviantart.com/gallery/?catpath=/'
	# 
	# response = requests.get(url)
	# 
	# foo = bs4.BeautifulSoup(response.text, 'html.parser')
	# linked_uris = set(iter_uris(foo, url))
	
	# for i in linked_uris:
	# 	if i.startswith('http://joycall3.deviantart.com/art/'):
	# 		print(i)
	
	# for i in linked_uris:
	# 	if i.startswith('http://joycall3.deviantart.com/gallery/'):
	# 		print(i)
	
	for i in walk_galleries():
		yield i
		


main()
