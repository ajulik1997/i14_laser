## A simple python file that demonstrates how to communicate with the server

import socket

host = socket.gethostname()
port = 14000

try:
	clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientsocket.connect((host, port))
except Exception as e:
	print(e)
	clientsocket.close()
	clientsocket = socket.socket()
	clientsocket.connect((host, port))

while True:
	mssg = input('SEND MESSAGE TO SERVER: ')
	clientsocket.send((mssg+'\r\n').encode())
	print('RECEIVED MESSAGE:', clientsocket.recv(1024).decode('ascii'))
