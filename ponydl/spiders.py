import bs4, requests, urllib.parse, datetime
from . import caches, util


class Requester:
	def __init__(self, cache : caches.Cache):
		self._cache = cache
	
	def get(self, uri : str, *, success_max_age : datetime.timedelta = None, failure_max_age : datetime.timedelta = None):
		def value_fn():
			util.log('Requesting page: {}', uri)
			
			return requests.get(uri)
		
		def max_age_fn(cached_value : requests.Response):
			if cached_value.ok:
				return success_max_age
			else:
				return failure_max_age
		
		return self._cache.get(uri, value_fn, max_age_by_cached_value_fn = max_age_fn)


class Page:
	def __init__(self, uri : str, soup : bs4.BeautifulSoup):
		self.uri = uri
		self.soup = soup
	
	def resolve_link(self, uri : str):
		return urllib.parse.urljoin(self.uri, uri)


def processor(*, success_max_age : datetime.timedelta = None, failure_max_age : datetime.timedelta = datetime.timedelta(hours = 1)):
	def decorator(wrapped_fn):
		return wrapped_fn, success_max_age, failure_max_age
	
	return decorator


class Spider:
	def __init__(self, requester : Requester):
		self._requester = requester
		
		# Element type: (processor_fn, uri : str)
		self._walked_uris = set()
		
		# Element type: (processor_fn, uri : str)
		self._queue = []
	
	def enqueue(self, processor, uri : str):
		request = processor, uri
		
		if request not in self._walked_uris:
			self._walked_uris.add(request)
			self._queue.append(request)
	
	def run(self):
		while self._queue:
			(processor_fn, success_max_age, failure_max_age), uri = self._queue.pop(0)
			response = self._requester.get(uri, success_max_age = success_max_age, failure_max_age = failure_max_age)
			
			if not response.ok:
				util.log('Error downloading page {}: {}', uri, response.status_code)
			else:
				soup = bs4.BeautifulSoup(response.text, 'html.parser')
				
				util.log('Processing with {}: {}', processor_fn.__name__, uri)
				
				processor_fn(Page(uri, soup))
