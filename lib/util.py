import sys, time, contextlib


def log(message, *args):
	print(message.format(*args), file = sys.stderr)


@contextlib.contextmanager
def timed(label : str):
	now = time.time()
	
	yield
	
	log('{}: {:.2f}', label, time.time() - now)
