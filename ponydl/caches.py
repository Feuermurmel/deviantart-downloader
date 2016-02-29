import sqlite3, pickle, datetime, gzip


class PersistentDict:
	def __init__(self, path):
		self._connection = sqlite3.connect(path)
		
		self._connection.execute('PRAGMA busy_timeout = 1000000000')
		
		with self._connection as cursor:
			cursor.execute('create table if not exists entries(key, value, primary key (key))')
	
	def set(self, key : str, value):
		with self._connection:
			cursor = self._connection.cursor()
			cursor.execute('insert or replace into entries (key, value) values (:key, :value)', dict(key = key, value = gzip.compress(pickle.dumps(value))))
	
	def get(self, key : str, default = None):
		with self._connection:
			cursor = self._connection.cursor()
			
			cursor.execute('select value from entries where key = :key', dict(key = key))
			rows = cursor.fetchall()
			
			if rows:
				(value,), = rows
				
				return pickle.loads(gzip.decompress(value))
			else:
				return default
				

class Cache:
	def __init__(self, dict : PersistentDict):
		self._dict = dict
	
	def get(self, key : str, value_fn : callable, *, max_age_by_cached_value_fn : callable = None):
		now = datetime.datetime.now()
		result = self._dict.get(key)
		
		if result is not None:
			timestamp, value = result
			max_age = max_age_by_cached_value_fn(value)
			
			if max_age is None or now - timestamp < max_age:
				return value
		
		value = value_fn()
		entry = now, value
		
		self._dict.set(key, entry)
		
		return value
