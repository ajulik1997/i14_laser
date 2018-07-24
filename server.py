###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summmer 2018                                                  ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

##### IMPORTS #################################################################

import socket                           ## access to BSD socket interface
#import os      # depreciated
import atexit                           ## gracefully close at exit
from datetime import datetime           ## UTC time for logging purposes
from threading import Thread            ## for threaded server
from externalParser import parse        ## EXTERNAL RULEBOOK
from errors import errno                ## EXTERNAL ERROR DICTIONARY

##### LOGGING AND RECOVERY DETECTION ##########################################

## depreciated: allowed for logging and crash detection
## to enable, remove all single (#) hashes before commented lines

#log = open('errlog.txt', mode='a', buffering=1)
#if os.path.isfile('LOCK'):
#   log.write(str(datetime.utcnow())+" RECOVERED FROM UNEXPECTED SHUTDOWN"+'\n')
#else:
#   open('LOCK', 'w').close()

##### HOST AND PORT SETUP #####################################################

host = socket.gethostname()
port = 14000

##### RESERVE SOCKET FOR PROCESS ##############################################

## reserve a socket and bind to it, close if this is not possible

try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((host, port))
except socket.error as error:
    print(str(datetime.utcnow())+" SOCKET ERROR: "+str(error))
    #log.write(str(datetime.utcnow())+" SOCKET ERROR: "+str(error)+'\n')
    raise

##### RESPONSE HANDLER ########################################################

def handleResponse(data):
    '''
    Simple function that tests the valid of received data before parsing
    
    Arguments:
        data <str> - data received from socket to be tested
    
    Returns:
        Resulting string from parsed and executed arguments
        Error codes (see local file errors.txt)
    '''
    if len(data) <= 2: return errno('10')
    if len(data) >= 128: return errno('11')
    if data[-2:] != '\r\n': return errno('12')
    
    words = [word for word in data[:-2].split(' ') if len(word) != 0]
    if len(words) == 0: return errno('13')
    if len(words) >= 8: return errno('14')
    
    return parse(words)

##### THREADED SERVER #########################################################
    
class connection(Thread):
    '''Simple threaded server derived from Thread class'''
    def __init__(self, socket, address):
        '''
        Init function for threaded server
        
        Arguments:
            self <connection> - reference to the current instance of the class
            socket <socket.socket> - reference to the opened socket
            address <tuple> - address and port number of incoming connection
        
        Returns:
            none
        '''
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.start()

    def run(self):
        '''
        Starts the thread that will handle communication with connected client:
            - in an infinite loop (terminated only by a connection reset error)
                - receives a maximum of 1024 bytes from client
                - send message to handleResponse --> Parser --> Some action
                - this will return a response which will be sent to client
                - if there is not data, the connection is closed and loop exits
            - on ConnectionResetError
                - closed connection is logged
                - control is returned to listener for a new connection
        '''
        try:
            while True:
                data = self.sock.recv(1024)
                if not data: raise ConnectionResetError
                self.sock.send(handleResponse(data.decode('ascii')))
        except ConnectionResetError:
            print(str(datetime.utcnow())+" CONNECTION CLOSED: "+self.addr[0]+':'+str(self.addr[1]))
            #log.write(str(datetime.utcnow())+" CONNECTION CLOSED: "+address[0]+':'+str(address[1])+'\n')

##### CONNECTION LISTENER #####################################################

serversocket.listen(1)                      ## only allows for one connection
print(str(datetime.utcnow())+" SERVER STARTED")
#log.write(str(datetime.utcnow())+" SERVER STARTED"+'\n')
while True:                         ## infinite loop which should never exit
    clientsocket, address = serversocket.accept()   ## accept connection
    print(str(datetime.utcnow())+" CONNECTION ESTABLISHED: "+address[0]+':'+str(address[1]))
    #log.write(str(datetime.utcnow())+" CONNECTION ESTABLISHED: "+address[0]+':'+str(address[1])+'\n')
    connection(clientsocket, address)   ## start server with details of client

##### EXIT HANDLER ############################################################

@atexit.register
def cleanup():
    print(str(datetime.utcnow())+" SERVER CLOSED SAFELY")
    #log.write(str(datetime.utcnow())+" SERVER CLOSED SAFELY"+'\n')
    #log.close()
    #os.remove('LOCK')
