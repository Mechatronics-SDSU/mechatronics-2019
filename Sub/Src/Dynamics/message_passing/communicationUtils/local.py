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
	Initializes the writer. Accepts a dictionary, writes whatever values we need
	to whatever key the user wants
	'''
	def __init__(self, volatile_memory):
		'''
		Initializes the writer
		Parameters:
			volatile_memory: The dictionary to "write" messages to and store in.
		Returns:
			N/A
		'''
		self.MEM=volatile_memory

	def write(self, msg, register):
		'''
		Writes the message desired to the key desired within the dictionary.
		Automatically creates the key if not found
		Parameters:
			msg:The message we want to "write". Essentially the value for the
				desired key we set in the dictionary
			register:The key to set the message to so the user can grab or
					 "read" it later
		Returns:
			N/A
		'''
		self.MEM[register]=msg
