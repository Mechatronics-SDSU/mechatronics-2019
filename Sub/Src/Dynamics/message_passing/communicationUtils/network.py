
class publisher(object):
	def __init__(self, ip_router):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		'''
		self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def publish(self, address, msg, type="UDP"):
		if type.upper() == "TCP":
			raise IOError(type, 'Functionality not implemented')
		return self.UDP_socket.sendto(msg, address)
		
class subscriber(object):
	def __init__(self, ip_router):
		'''
		Ip router is dictionary. key: ip address value: list of ports
		further segregation in types UDP or TCP
		'''
		self.UDP_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TCP_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def subscribe(self, address):
		'''
		Subscribes to address provided
		'''
		self.UDP_socket.bind(address)
		data, addr = sock.recvfrom(1024)
		
		return data
