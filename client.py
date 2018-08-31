###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summer 2018                                                   ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

## A simple python file that demonstrates how to communicate with server.py

##### IMPORTS #################################################################

import socket

##### HOST AND PORT SETUP #####################################################

host = socket.gethostname()     ## CHANGE THIS TO IP OR HOSTNAME OF SERVER
port = 14000

##### ATTEMPT TO CONNECT TO SERVER ############################################

try:    ## create client socket and bind to server
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((host, port))
except Exception as e:  ## socket may be left open from a crashed session
    print(e)
    clientsocket.close()    ## close socket and recreate it
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((host, port))  ## attempt to connect again

##### INFINITE LOOP FOR SENDING AND RECEIVING MESSAGES ########################

while True:
    msg = input('SEND MESSAGE TO SERVER: ')
    if msg == 'exit':
        clientsocket.close()
    else:
        clientsocket.send((msg+'\r\n').encode(encoding='ascii'))
        print('RECEIVED MESSAGE:', clientsocket.recv(1024).decode('ascii'))
