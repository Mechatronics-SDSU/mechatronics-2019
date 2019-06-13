import socket

class publisher(object):
	def __init__(self, ip_router):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		'''
		self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def publish(self, msg, address, type = "udp"):
		#host = address[0]
		#type = host[0:3]
		host = list(address.keys())[0]
		port = address[host]
		if type.upper() == "TCP":
			self.TCP_socket.connect((address))
			self.TCP_socket.send(msg.encode)
			#raise IOError(type, 'Functionality not implemented')
		else:
			self.UDP_socket.sendto(msg.encode(), (host, port))

class subscriber(object):
	def __init__(self, ip_router):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		further segregation in types UDP or TCP
		'''
		self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def subscribe(self, address, type = "udp"):
		'''
		Subscribes to address provided
		'''
		#host = address[0]
		#type = host[0:3]
		if type.upper() == "TCP":
			self.TCP_socket.bind((address))
			(cl, addr) = self.TCP_socket.accept()
			data = cl.recv(1024).decode()
			return data

		else:
			host = list(address.keys())[0]
			port = address[host]
			self.UDP_socket.bind((host, port))
			data, addr = self.UDP_socket.recvfrom(1024)
			return data.decode()
