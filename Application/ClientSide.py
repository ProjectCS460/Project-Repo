# Ticket App Client V1
# VERSION 1: 	Handles connection to ServerSide and ready for client-side UI
# AUTHOR: 		JacobT2006
# CREATED: 		04/9/2026
# VERSION 2:
# AUTHOR: 		jzabawski3453 & MysticalSkeptic
# CREATED: 		04/9/2026



#!/usr/bin/python3
from socket import *
import sys

#------------------------------------------------------------
# Server connection

serverSocket = None
host = "10.0.2.15"                                   # Change to server IP if needed
admin_authenticated = False

def connect_to_server(host, port=13000):
    """Establish connection to ticket server"""
    global serverSocket

    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((host, port))
        print("* | Successfully connected to server\n")
        return True
    except ConnectionRefusedError:
        print("* | ERROR: Could not connect to server - connection refused\n")
        print("* | Ensure server is running on {}:{}\n".format(host, port))
        return False
    except socket.timeout:
        print("* | ERROR: Connection to server timed out\n")
        return False
    except Exception as e:
        print(f"* | ERROR: Connection failed - {e}\n")
        return False

def send_request(message):
    """Send request to server"""
    global serverSocket

    if serverSocket is None:
        print("* | ERROR: Not connected to server\n")
        return None

    try:
        serverSocket.send(message.encode())
        print(f"* | Sent: {message.strip()}\n")
        return True
    except Exception as e:
        print(f"* | ERROR: Failed to send message - {e}\n")
        return False

def receive_response():
    """Receive response from server"""
    global serverSocket

    if serverSocket is None:
        print("* | ERROR: Not connected to server\n")
        return None

    try:
        response = serverSocket.recv(4096).decode()
        if response:
            print(f"* | Received: {response.strip()}\n")
            return response
        else:
            print("* | ERROR: Server closed connection\n")
            return None
    except Exception as e:
        print(f"* | ERROR: Failed to receive message - {e}\n")
        return None

def disconnect_from_server():
    """Close connection to server"""
    global serverSocket

    if serverSocket is not None:
        try:
            serverSocket.close()
            serverSocket = None
            print("* | Disconnected from server\n")
        except Exception as e:
            print(f"* | ERROR: Failed to disconnect - {e}\n")

#------------------------------------------------------------
# Customer Functions

def create_ticket():
    """Customer: Create a new ticket"""
    print("\n===== CREATE NEW TICKET =====")

    # INPUT: Customer name
    name = input("* | Enter your name: ").strip()
    if not name:
        print("* | ERROR: Name cannot be empty\n")
        return

    # INPUT: Customer email
    email = input("* | Enter your email: ").strip()
    if not email or "@" not in email:
        print("* | ERROR: Invalid email format\n")
        return

    # INPUT: Short description
    short_description = input("* | Enter ticket subject/topic: ").strip()
    if not short_description:
        print("* | ERROR: Subject cannot be empty\n")
        return

    message = f"CREATE_TICKET | {name} | {email} | {short_description}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Ticket created successfully!\n")
        else:
            print("* | ✗ Failed to create ticket\n")

def check_ticket_status():
    """Customer: Check status of own ticket"""
    print("\n===== CHECK TICKET STATUS =====")

    # INPUT: Ticket ID
    ticket_id = input("* | Enter ticket ID: ").strip()
    if not ticket_id:
        print("* | ERROR: Ticket ID cannot be empty\n")
        return

    # INPUT: Email verification
    email = input("* | Enter your email (for verification): ").strip()
    if not email or "@" not in email:
        print("* | ERROR: Invalid email format\n")
        return

    message = f"CHECK_STATUS | {ticket_id} | {email}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Status retrieved\n")
        else:
            print("* | ✗ Failed to check status\n")

def view_my_tickets():
    """Customer: View all own tickets"""
    print("\n===== VIEW MY TICKETS =====")

    # INPUT: Email
    email = input("* | Enter your email: ").strip()
    if not email or "@" not in email:
        print("* | ERROR: Invalid email format\n")
        return

    message = f"VIEW_MY_TICKETS | {email}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Tickets retrieved\n")
        else:
            print("* | ✗ Failed to retrieve tickets\n")

def filter_my_tickets():
    """Customer: Filter own tickets by status"""
    print("\n===== FILTER MY TICKETS =====")

    # INPUT: Email
    email = input("* | Enter your email: ").strip()
    if not email or "@" not in email:
        print("* | ERROR: Invalid email format\n")
        return

    # INPUT: Status filter
    print("* | Available statuses: open, closed, in_progress, pending")
    status = input("* | Enter status to filter by: ").strip().lower()
    if status not in ["open", "closed", "in_progress", "pending"]:
        print("* | ERROR: Invalid status\n")
        return

    message = f"FILTER_MY_TICKETS | {email} | {status}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Filtered tickets retrieved\n")
        else:
            print("* | ✗ Failed to filter tickets\n")

#------------------------------------------------------------
# Admin Functions

def admin_login():
    """Admin: Authenticate as admin"""
    global admin_authenticated

    print("\n===== ADMIN LOGIN =====")

    # INPUT: Username
    username = input("* | Enter admin username: ").strip()
    if not username:
        print("* | ERROR: Username cannot be empty\n")
        return

    # INPUT: Password
    password = input("* | Enter admin password: ").strip()
    if not password:
        print("* | ERROR: Password cannot be empty\n")
        return

    message = f"ADMIN_LOGIN | {username} | {password}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            admin_authenticated = True
            print("* | ✓ Admin authentication successful!\n")
        else:
            print("* | ✗ Authentication failed\n")

def admin_logout():
    """Admin: Logout from admin session"""
    global admin_authenticated

    if not admin_authenticated:
        print("* | ERROR: Not logged in as admin\n")
        return

    message = "ADMIN_LOGOUT\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            admin_authenticated = False
            print("* | ✓ Admin logout successful\n")
        else:
            print("* | ✗ Logout failed\n")

def view_all_tickets():
    """Admin: View all tickets in database"""
    global admin_authenticated

    if not admin_authenticated:
        print("* | ERROR: Admin authentication required\n")
        return

    print("\n===== VIEW ALL TICKETS =====")

    message = "VIEW_ALL_TICKETS\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ All tickets retrieved\n")
        else:
            print("* | ✗ Failed to retrieve tickets\n")

def filter_tickets():
    """Admin: Filter all tickets by status"""
    global admin_authenticated

    if not admin_authenticated:
        print("* | ERROR: Admin authentication required\n")
        return

    print("\n===== FILTER ALL TICKETS =====")

    # INPUT: Status filter
    print("* | Available statuses: open, closed, in_progress, pending")
    status = input("* | Enter status to filter by: ").strip().lower()
    if status not in ["open", "closed", "in_progress", "pending"]:
        print("* | ERROR: Invalid status\n")
        return

    message = f"FILTER_TICKETS | {status}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Filtered tickets retrieved\n")
        else:
            print("* | ✗ Failed to filter tickets\n")

def search_ticket():
    """Admin: Search for specific ticket by ID"""
    global admin_authenticated

    if not admin_authenticated:
        print("* | ERROR: Admin authentication required\n")
        return

    print("\n===== SEARCH TICKET =====")

    # INPUT: Ticket ID
    ticket_id = input("* | Enter ticket ID to search: ").strip()
    if not ticket_id.isdigit():
        print("* | ERROR: Invalid ticket ID format\n")
        return

    message = f"SEARCH_TICKET | {ticket_id}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Ticket found\n")
        else:
            print("* | ✗ Ticket not found\n")

def update_ticket():
    """Admin: Update ticket status and description"""
    global admin_authenticated

    if not admin_authenticated:
        print("* | ERROR: Admin authentication required\n")
        return

    print("\n===== UPDATE TICKET =====")

    # INPUT: Ticket ID
    ticket_id = input("* | Enter ticket ID to update: ").strip()
    if not ticket_id.isdigit():
        print("* | ERROR: Invalid ticket ID format\n")
        return

    # INPUT: New status
    print("* | Available statuses: open, closed, in_progress, pending")
    new_status = input("* | Enter new status: ").strip().lower()
    if new_status not in ["open", "closed", "in_progress", "pending"]:
        print("* | ERROR: Invalid status\n")
        return

    # INPUT: Long description/notes
    long_description = input("* | Enter admin notes/description: ").strip()
    if not long_description:
        print("* | ERROR: Description cannot be empty\n")
        return

    message = f"UPDATE_TICKET | {ticket_id} | {new_status} | {long_description}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Ticket updated successfully!\n")
        else:
            print("* | ✗ Failed to update ticket\n")

def view_by_name():
    """Admin: View tickets filtered by customer name"""
    global admin_authenticated

    if not admin_authenticated:
        print("* | ERROR: Admin authentication required\n")
        return

    print("\n===== VIEW TICKETS BY CUSTOMER NAME =====")

    # INPUT: Customer name
    customer_name = input("* | Enter customer name: ").strip()
    if not customer_name:
        print("* | ERROR: Customer name cannot be empty\n")
        return

    message = f"VIEW_BY_NAME | {customer_name}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Tickets retrieved\n")
        else:
            print("* | ✗ Failed to retrieve tickets\n")

def view_by_id():
    """Admin: View full details of ticket by ID"""
    global admin_authenticated

    if not admin_authenticated:
        print("* | ERROR: Admin authentication required\n")
        return

    print("\n===== VIEW TICKET DETAILS BY ID =====")

    # INPUT: Ticket ID
    ticket_id = input("* | Enter ticket ID: ").strip()
    if not ticket_id.isdigit():
        print("* | ERROR: Invalid ticket ID format\n")
        return

    message = f"VIEW_BY_ID | {ticket_id}\n"

    if send_request(message):
        response = receive_response()
        if response and "SUCCESS" in response:
            print("* | ✓ Ticket details retrieved\n")
        else:
            print("* | ✗ Failed to retrieve ticket details\n")

#------------------------------------------------------------
# Main Menu

def display_customer_menu():
    """Display customer menu options"""
    print("\n" + "="*50)
    print("         TICKET SYSTEM - CUSTOMER MENU")
    print("="*50)
    print("1. Create a new ticket")
    print("2. View my tickets")
    print("3. Check ticket status")
    print("4. Filter my tickets by status")
    print("5. Switch to admin login")
    print("6. Exit")
    print("="*50)

def display_admin_menu():
    """Display admin menu options"""
    print("\n" + "="*50)
    print("         TICKET SYSTEM - ADMIN MENU")
    print("="*50)
    print("1. View all tickets")
    print("2. Filter tickets by status")
    print("3. Search for ticket by ID")
    print("4. Update ticket status and notes")
    print("5. View tickets by customer name")
    print("6. View full ticket details by ID")
    print("7. Create a ticket (on behalf of customer)")
    print("8. Logout")
    print("9. Exit")
    print("="*50)

def customer_menu():
    """Customer menu loop"""
    while True:
        display_customer_menu()
        choice = input("* | Enter your choice (1-6): ").strip()

        if choice == "1":
            create_ticket()
        elif choice == "2":
            view_my_tickets()
        elif choice == "3":
            check_ticket_status()
        elif choice == "4":
            filter_my_tickets()
        elif choice == "5":
            admin_login()
            if admin_authenticated:
                admin_menu()
        elif choice == "6":
            print("\n* | Thank you for using the Ticket System!")
            break
        else:
            print("* | ERROR: Invalid choice. Please enter 1-6\n")

def admin_menu():
    """Admin menu loop"""
    global admin_authenticated

    while admin_authenticated:
        display_admin_menu()
        choice = input("* | Enter your choice (1-9): ").strip()

        if choice == "1":
            view_all_tickets()
        elif choice == "2":
            filter_tickets()
        elif choice == "3":
            search_ticket()
        elif choice == "4":
            update_ticket()
        elif choice == "5":
            view_by_name()
        elif choice == "6":
            view_by_id()
        elif choice == "7":
            create_ticket()
        elif choice == "8":
            admin_logout()
            break
        elif choice == "9":
            print("\n* | Thank you for using the Ticket System!")
            disconnect_from_server()
            sys.exit(0)
        else:
            print("* | ERROR: Invalid choice. Please enter 1-9\n")

#------------------------------------------------------------
# Main client initialization

def main():
    """Initialize client and connect to server"""
    print("* Ticket App Client V1\n")

    # Connect to server
    if not connect_to_server(host):
        print("* | Exiting client\n")
        sys.exit(1)

    print("* | Client ready to communicate with server\n")

    # Start customer menu
    try:
        customer_menu()
    except KeyboardInterrupt:
        print("\n* | Shutting down client\n")
    finally:
        disconnect_from_server()

#------------------------------------------------------------

if __name__ == "__main__":
    main()
