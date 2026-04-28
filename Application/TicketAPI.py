"""
Ticket System API - Bridge between CLI, HTML Frontend, and Server
Provides clean functions that can be called from any interface (HTML)
Handles all client-server communication
"""

from socket import *
import sys

#------------------------------------------------------------
# Global Connection Management

_server_socket = None
_admin_authenticated = False
_current_email = ""

def connect(host="127.0.0.1", port=13000):
    """
    Establish connection to ticket server
    Returns: (success: bool, message: str)
    """
    global _server_socket

    try:
        _server_socket = socket(AF_INET, SOCK_STREAM)
        _server_socket.connect((host, port))
        return (True, "Connected to server")
    except ConnectionRefusedError:
        return (False, "Server refused connection - ensure server is running on {}:{}".format(host, port))
    except Exception as e:
        return (False, "Connection failed: {}".format(str(e)))

def disconnect():
    """
    Close connection to ticket server
    Returns: (success: bool, message: str)
    """
    global _server_socket

    if _server_socket is not None:
        try:
            _server_socket.close()
            _server_socket = None
            return (True, "Disconnected from server")
        except Exception as e:
            return (False, "Disconnect error: {}".format(str(e)))
    return (False, "Not connected to server")

def _send_command(command_str):
    """
    Send command to server and receive response
    Returns: (success: bool, response: str)
    """
    global _server_socket

    if _server_socket is None:
        return (False, "Not connected to server")

    try:
        _server_socket.send(command_str.encode())
        response = _server_socket.recv(4096).decode()
        return (True, response.strip())
    except Exception as e:
        return (False, "Communication error: {}".format(str(e)))

#------------------------------------------------------------
# Customer API Functions

def create_ticket(name, email, description):
    """
    Create a new support ticket
    Args:
        name (str): Customer name
        email (str): Customer email
        description (str): Short description of issue
    Returns: (success: bool, ticket_id: str or None, message: str)
    """
    global _current_email
    _current_email = email

    if not all([name, email, description]):
        return (False, None, "All fields are required")

    message = f"CREATE_TICKET | {name} | {email} | {description}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        # Extract ticket ID from response
        try:
            ticket_id = response.split("|")[-1].strip()
            return (True, ticket_id, f"Ticket created: {ticket_id}")
        except:
            return (True, None, response)
    else:
        return (False, None, response)

def check_ticket_status(ticket_id, email):
    """
    Check status of a specific ticket
    Args:
        ticket_id (str): Ticket ID to check
        email (str): Email for verification (must match ticket owner)
    Returns: (success: bool, data: dict or None, message: str)
    """
    if not all([ticket_id, email]):
        return (False, None, "Ticket ID and email are required")

    message = f"CHECK_STATUS | {ticket_id} | {email}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response, "Status retrieved")
    else:
        return (False, None, response)

def view_my_tickets(email):
    """
    Retrieve all tickets for a customer email
    Args:
        email (str): Customer email
    Returns: (success: bool, tickets: str or None, message: str)
    """
    global _current_email
    _current_email = email

    if not email:
        return (False, None, "Email is required")

    message = f"VIEW_MY_TICKETS | {email}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response, "Tickets retrieved")
    else:
        return (False, None, response)

def filter_my_tickets(email, status):
    """
    Filter customer tickets by status
    Args:
        email (str): Customer email
        status (str): Status to filter (open, closed, in_progress, pending)
    Returns: (success: bool, tickets: str or None, message: str)
    """
    if not all([email, status]):
        return (False, None, "Email and status are required")

    if status.lower() not in ["open", "closed", "in_progress", "pending"]:
        return (False, None, "Invalid status. Must be: open, closed, in_progress, or pending")

    message = f"FILTER_MY_TICKETS | {email} | {status}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response, "Filtered tickets retrieved")
    else:
        return (False, None, response)

#------------------------------------------------------------
# Admin API Functions

def admin_login(username, password):
    """
    Authenticate as admin
    Args:
        username (str): Admin username
        password (str): Admin password
    Returns: (success: bool, message: str)
    """
    global _admin_authenticated

    if not all([username, password]):
        return (False, "Username and password are required")

    message = f"ADMIN_LOGIN | {username} | {password}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        _admin_authenticated = True
        return (True, "Admin authentication successful")
    else:
        _admin_authenticated = False
        return (False, response)

def admin_logout():
    """
    Logout from admin session
    Returns: (success: bool, message: str)
    """
    global _admin_authenticated

    if not _admin_authenticated:
        return (False, "Not logged in as admin")

    message = "ADMIN_LOGOUT\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        _admin_authenticated = False
        return (True, "Admin logout successful")
    else:
        return (False, response)

def view_all_tickets():
    """
    View all tickets in database (admin only)
    Returns: (success: bool, tickets: str or None, message: str)
    """
    if not _admin_authenticated:
        return (False, None, "Admin authentication required")

    message = "VIEW_ALL_TICKETS\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response, "All tickets retrieved")
    else:
        return (False, None, response)

def filter_tickets(status):
    """
    Filter all tickets by status (admin only)
    Args:
        status (str): Status to filter (open, closed, in_progress, pending)
    Returns: (success: bool, tickets: str or None, message: str)
    """
    if not _admin_authenticated:
        return (False, None, "Admin authentication required")

    if not status:
        return (False, None, "Status is required")

    if status.lower() not in ["open", "closed", "in_progress", "pending"]:
        return (False, None, "Invalid status. Must be: open, closed, in_progress, or pending")

    message = f"FILTER_TICKETS | {status}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response, "Filtered tickets retrieved")
    else:
        return (False, None, response)

def search_ticket(ticket_id):
    """
    Search for specific ticket by ID (admin only)
    Args:
        ticket_id (str): Ticket ID to search for
    Returns: (success: bool, ticket: str or None, message: str)
    """
    if not _admin_authenticated:
        return (False, None, "Admin authentication required")

    if not ticket_id:
        return (False, None, "Ticket ID is required")

    message = f"SEARCH_TICKET | {ticket_id}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response, "Ticket found")
    else:
        return (False, None, response)

def update_ticket(ticket_id, new_status, description):
    """
    Update ticket status and description (admin only)
    Args:
        ticket_id (str): Ticket ID to update
        new_status (str): New status (open, closed, in_progress, pending)
        description (str): Admin notes/description
    Returns: (success: bool, message: str)
    """
    if not _admin_authenticated:
        return (False, "Admin authentication required")

    if not all([ticket_id, new_status, description]):
        return (False, "Ticket ID, status, and description are required")

    if new_status.lower() not in ["open", "closed", "in_progress", "pending"]:
        return (False, "Invalid status. Must be: open, closed, in_progress, or pending")

    message = f"UPDATE_TICKET | {ticket_id} | {new_status} | {description}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response)
    else:
        return (False, response)

def view_by_name(customer_name):
    """
    View tickets filtered by customer name (admin only)
    Args:
        customer_name (str): Customer name to search for
    Returns: (success: bool, tickets: str or None, message: str)
    """
    if not _admin_authenticated:
        return (False, None, "Admin authentication required")

    if not customer_name:
        return (False, None, "Customer name is required")

    message = f"VIEW_BY_NAME | {customer_name}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response, "Tickets retrieved")
    else:
        return (False, None, response)

def view_by_id(ticket_id):
    """
    View full details of ticket by ID (admin only)
    Args:
        ticket_id (str): Ticket ID to retrieve
    Returns: (success: bool, ticket: str or None, message: str)
    """
    if not _admin_authenticated:
        return (False, None, "Admin authentication required")

    if not ticket_id:
        return (False, None, "Ticket ID is required")

    message = f"VIEW_BY_ID | {ticket_id}\n"
    success, response = _send_command(message)

    if success and "SUCCESS" in response:
        return (True, response, "Ticket details retrieved")
    else:
        return (False, None, response)

def is_admin_authenticated():
    """
    Check if currently authenticated as admin
    Returns: bool
    """
    return _admin_authenticated

def is_connected():
    """
    Check if connected to server
    Returns: bool
    """
    return _server_socket is not None

#------------------------------------------------------------

if __name__ == "__main__":
    # Simple test to verify API works
    success, msg = connect()
    print(f"Connection: {msg}")

    if success:
        # Test customer function
        success, ticket_id, msg = create_ticket("John Doe", "john@example.com", "Test issue")
        print(f"Create ticket: {msg}")

        # Test customer view
        success, data, msg = view_my_tickets("john@example.com")
        print(f"View tickets: {msg}")
        if data:
            print(f"Data: {data}\n")

        disconnect()
