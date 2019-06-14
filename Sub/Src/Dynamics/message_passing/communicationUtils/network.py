import socket

class publisher(object):
	def __init__(self, ip_router, type):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		'''
		#self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		#self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.ip_router=ip_router
		self.type=type

	def publish(self, msg, key):

		tuple = self.ip_router[key]

		tuple[0].sendto(msg, key)

		'''
		if self.type.upper() == "TCP":

			self.TCP_socket.sendto(msg, address)
		else:
			self.UDP_socket.sendto(msg, address)
		'''

class subscriber(object):
	def __init__(self, ip_router, type):
		'''
		Ip router is dictionary. key: ip register value: list of ports
		further segregation in types UDP or TCP
		'''
		#self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ip_router=ip_router
		self.type=type


	def subscribe(self, key):
		'''
		Subscribes to register provided
		'''
		tuple = self.ip_router[key]
		data, addr = tuple[1].recvfrom(4096)
		return data
