'''
Copyright 2019, Mohammad Shafi & Christian Gould, All rights reserved

Authors: Christian Gould <christian.d.gould@gmail.com>
		 Mohammad Shafi <ma.shafi99@gmail.com>
Last Modified 06/13/2019
Description: Creates tools for all local communication, i.e. "reads" and writes.
			 Allows the user to directly pull or store data into ram via the use
			 of a dictionary, as insert and searches using the dictionary are big
			 O of N
'''
class reader(object):
	'''
	Reader class. Allows the user to pull data locally from memory. Prevents the need
	to publish or subscribe unecessarily when local data transfer would be faster
	'''
	def __init__(self, volatile_memory):
		'''
		Initializes the reader. Accepts a dictionary and lets the reader retrieve any data user
		wishes, so long as the key is stored within the dictionary.
		Parameters:
			volatile_memory: The dictionary containing all data to be read locally.
			Mapped using a key value pair.
		Returns:
			 N/A
		'''
		self.MEM=volatile_memory

	def read(self, register):
		'''
		Takes in the key for the data we want to read, returns value.
		Parameters:
			register: The key for what we want to read from the dictionary
		Returns:
			Value associated with the key, so long as it's in the dictionary
		'''
		return self.MEM[register]

class writer(object):
	'''
	Initializes the writer. 
	'''
	def __init__(self, volatile_memory):
		'''
		'''
		self.MEM=volatile_memory

	def write(self, msg, register):
		'''
		'''
		self.MEM[register]=msg
