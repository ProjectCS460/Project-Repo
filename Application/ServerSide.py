# Ticket App Server V1
# VERSION 1: 	Handles input from ClientSide and ticket data as well as login validation
# AUTHOR: 		JacobT2006
# CREATED: 		04/9/2026

#!/usr/sbin/python3
from socket import *
from _thread import *
from random import *

#------------------------------------------------------------
# User identification

users = {}  

def load_users(filename=LOGIN.csv):
    try:
        with open(filename, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != 3:
                    continue
                username, password, authority = row
                users[username] = {
                    "password": password,
                    "authority": authority.lower()
                }
        print("* User database loaded.")
    except FileNotFoundError:
        print("* | ERROR: User CSV file not found.")
        exit(1)
#------------------------------------------------------------
# Login validation

def validate_admin(username, password):
    if username in users:
        return users[username]["password"] == password and users[username]["authority"] == "admin"
    return False

def validate_basic_user(username, password):
    if username in users:
        return users[username]["password"] == password and users[username]["authority"] == "user"
    return False
#------------------------------------------------------------
# Load database

def load_data(filename=DATA.csv
	try:
		with open(filename, "") as file:
			
	except FileNotFoundError:
        print("* | ERROR: Data CSV file not found.")
        exit(1)
#------------------------------------------------------------
# Ticket actions

def create_ticket(fields):
    # fields = [name, email, short_description]
    # Placeholder: generate ticket ID, timestamp, save to DB
    return "SUCCESS | Ticket created | 1001\n"

def check_ticket_status(fields):
    # fields = [ticket_id, email]
    # Placeholder: verify ticket exists and email matches
    return "SUCCESS | Ticket found | STATUS: OPEN\n"

def admin_update_ticket(fields):
    # fields = [ticket_id, new_status, long_description]
    # Placeholder: update ticket in DB
    return "SUCCESS | Ticket updated\n"

def admin_view_all():
    # Placeholder: return all tickets
    return "SUCCESS | All tickets listed\n"

def admin_filter_status(fields):
    # fields = [status]
    # Placeholder: filter tickets by status
    return "SUCCESS | Filtered tickets\n"

def admin_search_ticket(fields):
    # fields = [ticket_id]
    # Placeholder: return ticket details
    return "SUCCESS | Ticket found\n"
#------------------------------------------------------------


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
#------------------------------------------------------------
# Connection socket

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
#------------------------------------------------------------
