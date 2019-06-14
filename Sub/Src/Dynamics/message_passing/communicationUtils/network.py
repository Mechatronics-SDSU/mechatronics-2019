import socket

class publisher(object):
	def __init__(self, ip_router):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		'''
		#self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		#self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.ip_router=ip_router

	def publish(self, msg, register):

		address  = self.ip_router[register]['address']
		pub_sock = self.ip_router[register]['sockets'][0]
		sub_sock = self.ip_router[register]['sockets'][1] #sub_sock for reference

		return 	pub_sock.sendto(msg, address)


class subscriber(object):
	def __init__(self, ip_router):
		'''
		Ip router is dictionary. key: ip register value: list of ports
		further segregation in types UDP or TCP
		'''
		#TODO double check format for json:

		#self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ip_router=ip_router
		self.type=type


	def subscribe(self, register):
		'''
		Subscribes to register provided
		'''

		#TODO double check format for json:
		if self.ip_router[register]['type']=='TCP':
			pass

		else:
			address  = self.ip_router[register]['address']
			pub_sock = self.ip_router[register]['sockets'][0]
			sub_sock = self.ip_router[register]['sockets'][1] #sub_sock for reference

			address  = self.ip_router[register]['address']
			pub_sock = self.ip_router[register]['sockets'][0]
			sub_sock = self.ip_router[register]['sockets'][1]

			data, addr = sub_sock.recvfrom(4096)

			return data
