class reader(object):
	def __init__(self, volatile_memory):
		'''
		'''
		self.MEM=volatile_memory

	def read(self, address):
		'''
		'''
		return self.MEM[address]

class writer(object):
	def __init__(self, volatile_memory):
		'''
		'''
		self.MEM=volatile_memory

	def write(self, address, msg):
		'''
		'''
		self.MEM[address]=msg
