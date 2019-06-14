class reader(object):
	def __init__(self, volatile_memory):
		'''
		accepts dictionary, returns value
		'''
		self.MEM=volatile_memory

	def read(self, register):
		'''
		'''
		return self.MEM[register]

class writer(object):
	def __init__(self, volatile_memory):
		'''
		'''
		self.MEM=volatile_memory

	def write(self, msg, register):
		'''
		'''
		self.MEM[register]=msg
