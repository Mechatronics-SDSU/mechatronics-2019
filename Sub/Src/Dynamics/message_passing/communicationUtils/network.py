import socket

class publisher(object):
	def __init__(self, ip_router, type):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		'''
		self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.ip_router=ip_router
		self.type=type

	def publish(self, msg, register):

		address = self.ip_router[register]

		if self.type.upper() == "TCP":

			self.TCP_socket.sendto(msg, address)
		else:
			self.UDP_socket.sendto(msg, address)

class subscriber(object):
	def __init__(self, ip_router, type):
		'''
		Ip router is dictionary. key: ip register value: list of ports
		further segregation in types UDP or TCP
		'''
		self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ip_router=ip_router
		self.type=type


	def subscribe(self, register):
		'''
		Subscribes to register provided
		'''
		address = self.ip_router[register]

		if self.type.upper() == "TCP":

			self.TCP_socket.bind(address)
			data, addr = self.TCP_socket.recvfrom(4096)

			return data

		else:

			self.UDP_socket.bind(address)
			data, addr = self.UDP_socket.recvfrom(4096)

			return data
