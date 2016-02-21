import bs4, requests, urllib.parse
from . import caches, util


class Requester:
	def __init__(self, cache : caches.Cache):
		self._cache = cache
	
	def get(self, uri : str):
		def fn():
			util.log('Requesting page: {}', uri)
			
			return requests.get(uri)
		
		return self._cache.get(uri, fn)


class Page:
	def __init__(self, uri : str, soup : bs4.BeautifulSoup):
		self.uri = uri
		self.soup = soup
	
	def resolve_link(self, uri : str):
		return urllib.parse.urljoin(self.uri, uri)


class Spider:
	def __init__(self, requester : Requester):
		self._requester = requester
		
		# Element type: (processor_fn, uri : str)
		self._walked_uris = set()
		
		# Element type: (processor_fn, uri : str)
		self._queue = []
	
	def enqueue(self, processor_fn : callable, uri : str):
		request = processor_fn, uri
		
		if request not in self._walked_uris:
			self._walked_uris.add(request)
			self._queue.append(request)
	
	def run(self):
		while self._queue:
			processor_fn, uri = self._queue.pop(0)
			response = self._requester.get(uri)
			
			if not response.ok:
				util.log('Error downloading page {}: {}', uri, response.status_code)
			else:
				soup = bs4.BeautifulSoup(response.text, 'html.parser')
				
				util.log('Processing with {}: {}', processor_fn.__name__, uri)
				
				processor_fn(Page(uri, soup))
