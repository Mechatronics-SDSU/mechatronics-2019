import socket

class publisher(object):
	def __init__(self, ip_router):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		'''
		self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def publish(self, address, msg, type="UDP"):
		if type.upper() == "TCP":
			self.TCP_socket.connect(address)
			self.TCP_socket.send(msg.encode())
			#raise IOError(type, 'Functionality not implemented')
		return self.UDP_socket.sendto(msg, address)

class subscriber(object):
	def __init__(self, ip_router):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		further segregation in types UDP or TCP
		'''
		self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def subscribe(self, address, type):
		'''
		Subscribes to address provided
		'''
		if type.upper() == "TCP":
			self.TCP_socket.bind(address)
			(cl, addr) = self.TCP_socket.accept()
			data = cl.recv(1024).decode()
			return data

		self.UDP_socket.bind(address)
		data, addr = self.UDP_socket.recvfrom(1024)

		return data
