# Ticket App Server V1
# VERSION 1: 	Handles input from ClientSide and ticket data as well as login validation
# AUTHOR: 		JacobT2006
# CREATED: 		04/9/2026

from socket import *
from _thread import *
from datetime import datetime
import csv
import os

#------------------------------------------------------------
# Global data structures

users = {}
tickets = {}
next_ticket_id = 1001

#------------------------------------------------------------
# User identification

def load_users(filename="LOGIN.csv"):
    """Load admin credentials from LOGIN.csv"""
    global users
    try:
        with open(filename, "r") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header if present
            for row in reader:
                if len(row) < 3:
                    continue
                username, password, authority = row[0], row[1], row[2].lower()
                users[username] = {
                    "password": password,
                    "authority": authority
                }
        print("* User database loaded.")
    except FileNotFoundError:
        print("* | ERROR: User CSV file not found.")
        exit(1)

#------------------------------------------------------------
# Login validation

def validate_admin(username, password):
    """Validate admin login credentials"""
    if username in users:
        return users[username]["password"] == password and users[username]["authority"] == "admin"
    return False

def validate_basic_user(email):
    """Validate basic user email exists in system"""
    for ticket_id, ticket in tickets.items():
        if ticket["email"] == email:
            return True
    return False

#------------------------------------------------------------
# Load ticket database

def load_data(filename="DATA.csv"):
    """Load existing tickets from DATA.csv"""
    global tickets, next_ticket_id
    try:
        with open(filename, "r") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header if present
            for row in reader:
                if len(row) < 7:
                    continue
                ticket_id = int(row[0])
                tickets[ticket_id] = {
                    "ticket_id": ticket_id,
                    "name": row[1],
                    "email": row[2],
                    "short_description": row[3],
                    "status": row[4],
                    "timestamp": row[5],
                    "long_description": row[6]
                }
                if ticket_id >= next_ticket_id:
                    next_ticket_id = ticket_id + 1
        print("* Ticket database loaded.")
    except FileNotFoundError:
        print("* | ERROR: Data CSV file not found.")
        exit(1)

def save_data(filename="DATA.csv"):
    """Save current tickets to DATA.csv"""
    try:
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ticket_id", "name", "email", "short_description", "status", "timestamp", "long_description"])
            for ticket_id, ticket in tickets.items():
                writer.writerow([
                    ticket["ticket_id"],
                    ticket["name"],
                    ticket["email"],
                    ticket["short_description"],
                    ticket["status"],
                    ticket["timestamp"],
                    ticket["long_description"]
                ])
        print("* Ticket database saved.")
    except Exception as e:
        print(f"* | ERROR: Failed to save data: {e}")

#------------------------------------------------------------
# Ticket actions

def create_ticket(fields):
    """Create a new ticket"""
    # fields = [name, email, short_description]
    global next_ticket_id
    
    if len(fields) < 3:
        return "ERROR | Invalid ticket creation format\n"
    
    name = fields[0]
    email = fields[1]
    short_description = fields[2]
    
    ticket_id = next_ticket_id
    next_ticket_id += 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    tickets[ticket_id] = {
        "ticket_id": ticket_id,
        "name": name,
        "email": email,
        "short_description": short_description,
        "status": "open",
        "timestamp": timestamp,
        "long_description": ""
    }
    
    save_data()
    return f"SUCCESS | TICKET_CREATED | {ticket_id}\n"

def check_ticket_status(fields):
    """Check status of a specific ticket by ID and email"""
    # fields = [ticket_id, email]
    
    if len(fields) < 2:
        return "ERROR | Invalid status check format\n"
    
    try:
        ticket_id = int(fields[0])
    except ValueError:
        return "ERROR | Invalid ticket ID format\n"
    
    email = fields[1]
    
    if ticket_id not in tickets:
        return "ERROR | Ticket not found\n"
    
    ticket = tickets[ticket_id]
    
    if ticket["email"] != email:
        return "ERROR | Unauthorized access - email does not match ticket owner\n"
    
    return f"SUCCESS | STATUS | {ticket_id} | {ticket['status']} | {ticket['timestamp']} | {ticket['long_description']}\n"

def view_my_tickets(fields):
    """View all tickets for a specific customer email"""
    # fields = [email]
    
    if len(fields) < 1:
        return "ERROR | Invalid view request format\n"
    
    email = fields[0]
    customer_tickets = []
    
    for ticket_id, ticket in tickets.items():
        if ticket["email"] == email:
            customer_tickets.append(f"{ticket['ticket_id']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']}")
    
    if not customer_tickets:
        return "SUCCESS | TICKET_LIST | No tickets found\n"
    
    ticket_list = " ; ".join(customer_tickets)
    return f"SUCCESS | TICKET_LIST | {ticket_list}\n"

def filter_my_tickets(fields):
    """Filter customer tickets by status"""
    # fields = [email, status]
    
    if len(fields) < 2:
        return "ERROR | Invalid filter format\n"
    
    email = fields[0]
    status = fields[1].lower()
    filtered_tickets = []
    
    for ticket_id, ticket in tickets.items():
        if ticket["email"] == email and ticket["status"].lower() == status:
            filtered_tickets.append(f"{ticket['ticket_id']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']}")
    
    if not filtered_tickets:
        return f"SUCCESS | FILTERED_LIST | No tickets with status '{status}' found\n"
    
    ticket_list = " ; ".join(filtered_tickets)
    return f"SUCCESS | FILTERED_LIST | {ticket_list}\n"

def admin_view_all():
    """View all tickets in database (admin only)"""
    all_tickets = []
    
    for ticket_id, ticket in tickets.items():
        all_tickets.append(f"{ticket['ticket_id']} | {ticket['name']} | {ticket['email']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']} | {ticket['long_description']}")
    
    if not all_tickets:
        return "SUCCESS | TICKET_LIST | Database is empty\n"
    
    ticket_list = " ; ".join(all_tickets)
    return f"SUCCESS | TICKET_LIST | {ticket_list}\n"

def admin_filter_tickets(fields):
    """Filter all tickets by status (admin only)"""
    # fields = [status]
    
    if len(fields) < 1:
        return "ERROR | Invalid filter format\n"
    
    status = fields[0].lower()
    filtered_tickets = []
    
    for ticket_id, ticket in tickets.items():
        if ticket["status"].lower() == status:
            filtered_tickets.append(f"{ticket['ticket_id']} | {ticket['name']} | {ticket['email']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']} | {ticket['long_description']}")
    
    if not filtered_tickets:
        return f"SUCCESS | FILTERED_LIST | No tickets with status '{status}' found\n"
    
    ticket_list = " ; ".join(filtered_tickets)
    return f"SUCCESS | FILTERED_LIST | {ticket_list}\n"

def admin_search_ticket(fields):
    """Search for specific ticket by ID (admin only)"""
    # fields = [ticket_id]
    
    if len(fields) < 1:
        return "ERROR | Invalid search format\n"
    
    try:
        ticket_id = int(fields[0])
    except ValueError:
        return "ERROR | Invalid ticket ID format\n"
    
    if ticket_id not in tickets:
        return "ERROR | Ticket not found\n"
    
    ticket = tickets[ticket_id]
    ticket_data = f"{ticket['ticket_id']} | {ticket['name']} | {ticket['email']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']} | {ticket['long_description']}"
    
    return f"SUCCESS | TICKET_FOUND | {ticket_data}\n"

def admin_update_ticket(fields):
    """Update ticket status and long description (admin only)"""
    # fields = [ticket_id, new_status, long_description]
    
    if len(fields) < 3:
        return "ERROR | Invalid update format\n"
    
    try:
        ticket_id = int(fields[0])
    except ValueError:
        return "ERROR | Invalid ticket ID format\n"
    
    if ticket_id not in tickets:
        return "ERROR | Ticket not found\n"
    
    new_status = fields[1].lower()
    long_description = fields[2]
    
    if new_status not in ["open", "closed", "in_progress", "pending"]:
        return "ERROR | Invalid status\n"
    
    tickets[ticket_id]["status"] = new_status
    tickets[ticket_id]["long_description"] = long_description
    
    save_data()
    return f"SUCCESS | TICKET_UPDATED | {ticket_id} | {new_status} | {long_description}\n"

def admin_view_by_name(fields):
    """View tickets filtered by customer name (admin only)"""
    # fields = [customer_name]
    
    if len(fields) < 1:
        return "ERROR | Invalid view format\n"
    
    customer_name = fields[0]
    matching_tickets = []
    
    for ticket_id, ticket in tickets.items():
        if customer_name.lower() in ticket["name"].lower():
            matching_tickets.append(f"{ticket['ticket_id']} | {ticket['name']} | {ticket['email']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']} | {ticket['long_description']}")
    
    if not matching_tickets:
        return f"SUCCESS | TICKET_LIST | No tickets found for customer '{customer_name}'\n"
    
    ticket_list = " ; ".join(matching_tickets)
    return f"SUCCESS | TICKET_LIST | {ticket_list}\n"

def admin_view_by_id(fields):
    """View full details of ticket by ID (admin only)"""
    # fields = [ticket_id]
    
    if len(fields) < 1:
        return "ERROR | Invalid view format\n"
    
    try:
        ticket_id = int(fields[0])
    except ValueError:
        return "ERROR | Invalid ticket ID format\n"
    
    if ticket_id not in tickets:
        return "ERROR | Ticket not found\n"
    
    ticket = tickets[ticket_id]
    ticket_data = f"ticket_id: {ticket['ticket_id']} | name: {ticket['name']} | email: {ticket['email']} | status: {ticket['status']} | timestamp: {ticket['timestamp']} | short_description: {ticket['short_description']} | long_description: {ticket['long_description']}"
    
    return f"SUCCESS | TICKET_FOUND | {ticket_data}\n"

#------------------------------------------------------------
# Client connection handler

def TicketThread(connectSocket):
    """Handle individual client connection"""
    print("* | Starting connection for service\n")
    
    admin_authenticated = False
    client_email = None
    
    while True:
        try:
            clientRequest = connectSocket.recv(1024).decode()
            
            if not clientRequest:
                break
            
            print(f"* | Received: {clientRequest.strip()}")
            
            # Parse client request
            parts = clientRequest.strip().split(" | ")
            command = parts[0].upper()
            fields = parts[1:] if len(parts) > 1 else []
            
            response = ""
            
            # Admin commands
            if command == "ADMIN_LOGIN":
                if len(fields) >= 2:
                    username = fields[0]
                    password = fields[1]
                    if validate_admin(username, password):
                        admin_authenticated = True
                        response = "SUCCESS | ADMIN_AUTHENTICATED\n"
                    else:
                        response = "ERROR | Invalid admin credentials\n"
                else:
                    response = "ERROR | Invalid login format\n"
            
            elif command == "ADMIN_LOGOUT":
                if admin_authenticated:
                    admin_authenticated = False
                    response = "SUCCESS | ADMIN_LOGOUT\n"
                else:
                    response = "ERROR | Not authenticated as admin\n"
            
            elif command == "VIEW_ALL_TICKETS":
                if admin_authenticated:
                    response = admin_view_all()
                else:
                    response = "ERROR | Unauthorized - admin access required\n"
            
            elif command == "FILTER_TICKETS":
                if admin_authenticated:
                    response = admin_filter_tickets(fields)
                else:
                    response = "ERROR | Unauthorized - admin access required\n"
            
            elif command == "SEARCH_TICKET":
                if admin_authenticated:
                    response = admin_search_ticket(fields)
                else:
                    response = "ERROR | Unauthorized - admin access required\n"
            
            elif command == "UPDATE_TICKET":
                if admin_authenticated:
                    response = admin_update_ticket(fields)
                else:
                    response = "ERROR | Unauthorized - admin access required\n"
            
            elif command == "VIEW_BY_NAME":
                if admin_authenticated:
                    response = admin_view_by_name(fields)
                else:
                    response = "ERROR | Unauthorized - admin access required\n"
            
            elif command == "VIEW_BY_ID":
                if admin_authenticated:
                    response = admin_view_by_id(fields)
                else:
                    response = "ERROR | Unauthorized - admin access required\n"
            
            # Customer commands
            elif command == "CREATE_TICKET":
                response = create_ticket(fields)
            
            elif command == "CHECK_STATUS":
                response = check_ticket_status(fields)
            
            elif command == "VIEW_MY_TICKETS":
                response = view_my_tickets(fields)
            
            elif command == "FILTER_MY_TICKETS":
                response = filter_my_tickets(fields)
            
            elif command == "DISCONNECT":
                response = "SUCCESS | DISCONNECTED\n"
                connectSocket.send(response.encode())
                break
            
            else:
                response = "ERROR | Unknown command\n"
            
            # Send response to client
            connectSocket.send(response.encode())
            print(f"* | Sent: {response.strip()}\n")
        
        except Exception as e:
            print(f"* | ERROR: {e}")
            response = f"ERROR | Server error: {str(e)}\n"
            try:
                connectSocket.send(response.encode())
            except:
                pass
            break
    
    connectSocket.close()
    print("* | Connection closed\n")

#------------------------------------------------------------
# Main server setup

def main():
    """Initialize server and handle connections"""
    host = "127.0.0.1"
    port = 13000
    
    # Load databases
    load_users()
    load_data()
    
    # Create server socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    
    print(f"* Server listening on {host}:{port}\n")
    
    try:
        while True:
            print("* | Waiting for client connection...\n")
            clientSocket, clientAddr = serverSocket.accept()
            print(f"* | Client connected from {clientAddr}\n")
            
            # Start new thread for client
            start_new_thread(TicketThread, (clientSocket,))
    
    except KeyboardInterrupt:
        print("\n* | Server shutting down...\n")
    finally:
        serverSocket.close()

#------------------------------------------------------------

if __name__ == "__main__":
    main()

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
