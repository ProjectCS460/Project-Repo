# Ticket App Server V1
# VERSION 1: 	Handles input from ClientSide and ticketing
# AUTHOR: 		JacobT2006
# CREATED: 		04/9/2026

#!/usr/sbin/python3
from socket import *
from _thread import *
from random import *

def TicketThread(connectSocket):
    print(" * | Starting connection for service \n")
	
    clientRequest=connectSocket.recv(1024).decode()
	print(clientRequest)
	# PlaceHolder for client response 




	while(true) #input message for loop from clientRequest
		#Placeholder for message stuffs
		break

	connectSocket.close()
    print(" * | Connection closed \n")

def serverMain():
	serverPort = 12345 #create a welcome TCP socket
	serverSocket= socket(AF_INET,SOCK_STREAM)
	#serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
	serverSocket.bind(("", serverPort))
	serverSocket.listen(1)
	print("* | The server is ready on port {serverPort}!")

	# Loop to forever accept client requests
	while True:
		#Create connection socket when sensing new connection request
		connectSocket,addr=serverSocket.accept()
		start_new_thread(numberGuessThread, (connectSocket,))
serverMain()
