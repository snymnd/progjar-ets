from socket import *
import socket
import os
import ssl
import logging
import multiprocessing
from http import HttpServer

httpserver = HttpServer()


class ProcessTheClient(multiprocessing.Process):
	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		multiprocessing.Process.__init__(self)

	def run(self):
		rcv=""
		while True:
			try:
				data = self.connection.recv(32)
				if data:
					d = data.decode()
					rcv=rcv+d
					if rcv[-2:]=='\r\n':
						hasil = httpserver.proses(rcv)
						hasil=hasil+"\r\n\r\n".encode()
						self.connection.sendall(hasil)
						rcv=""
						self.connection.close()
						break
				else:
					break
			except OSError as e:
				pass
		self.connection.close()




class Server(multiprocessing.Process):
	def __init__(self):
		self.the_clients = []
#------------------------------
		# self.hostname = hostname
		cert_location = os.getcwd() + '/certs/'
		self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		self.context.load_cert_chain(certfile=cert_location + 'domain.crt',
									 keyfile=cert_location + 'domain.key')
#---------------------------------

		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		multiprocessing.Process.__init__(self)

	def run(self):
		self.my_socket.bind(('0.0.0.0', 9000))
		self.my_socket.listen(1)
		while True:
			self.connection, self.client_address = self.my_socket.accept()
			try:
				self.secure_connection = self.context.wrap_socket(self.connection, server_side=True)
				logging.warning("connection from {}".format(self.client_address))
				clt = ProcessTheClient(self.connection, self.client_address)
				self.the_clients.append(clt)
				clt.daemon = True
				clt.start()
				self.connection.close()
			except ssl.SSLError as essl:
				print(str(essl))
				break


def main():
	svr = Server()
	svr.start()

if __name__=="__main__":
	main()

