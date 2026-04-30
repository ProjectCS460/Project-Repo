#!/usr/bin/python3
# Ticket App Server V1
# VERSION 1: 	Handles input from ClientSide and ticket data as well as login validation
# AUTHOR: 	JacobT2006
# CREATED: 	04/9/2026

from pathlib import Path
from socket import *
from _thread import start_new_thread
from datetime import datetime
import csv
import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

#------------------------------------------------------------
# Global data structures

users = {}
tickets = {}
next_ticket_id = 1001

serverSocket = None
server_thread = None
server_running = False
log_widget = None
host_value = "10.0.2.15"
port_value = 13000

#------------------------------------------------------------
# User identification
users_data = Path(__file__).parent / "Data" / "LOGIN.csv"

def is_header_row(row):
    if len(row) < 3:
        return False
    header_tokens = {cell.strip().lower() for cell in row}
    return "username" in header_tokens or "password" in header_tokens or "authority" in header_tokens


def load_users():
    """Load admin credentials from LOGIN.csv"""
    global users
    users.clear()
    try:
        with open(users_data, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or len(row) < 3:
                    continue
                if is_header_row(row):
                    continue
                username, password, authority = row[0].strip(), row[1].strip(), row[2].strip().lower()
                if username and password:
                    users[username] = {
                        "password": password,
                        "authority": authority
                    }
        append_log("* User database loaded.")
    except FileNotFoundError:
        append_log(f"* | ERROR: User CSV file not found at: {users_data}")
        messagebox.showerror("Server Error", f"User CSV file not found at: {users_data}")
        sys.exit(1)

#------------------------------------------------------------
# Login validation

def validate_admin(username, password):
    """Validate admin login credentials"""
    if username in users:
        return users[username]["password"] == password and users[username]["authority"] == "admin"
    return False

#------------------------------------------------------------
# Load ticket database

ticket_database = Path(__file__).parent / "Data" / "DATA.csv"

def load_data():
    """Load existing tickets from DATA.csv"""
    global tickets, next_ticket_id
    tickets.clear()
    next_ticket_id = 1001
    try:
        with open(ticket_database, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or len(row) < 7:
                    continue
                if is_header_row(row):
                    continue
                try:
                    ticket_id = int(row[0])
                except ValueError:
                    continue
                tickets[ticket_id] = {
                    "ticket_id": ticket_id,
                    "name": row[1].strip(),
                    "email": row[2].strip(),
                    "short_description": row[3].strip(),
                    "status": row[4].strip(),
                    "timestamp": row[5].strip(),
                    "long_description": row[6].strip()
                }
                if ticket_id >= next_ticket_id:
                    next_ticket_id = ticket_id + 1
        append_log("* Ticket database loaded.")
    except FileNotFoundError:
        append_log(f"* | WARNING: Data CSV not found at: {ticket_database}. Starting with empty ticket database.")
        # Empty DB is valid — don't exit


def save_data():
    """Save current tickets to DATA.csv"""
    try:
        with open(ticket_database, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ticket_id", "name", "email", "short_description", "status", "timestamp", "long_description"])
            for ticket_id, ticket in sorted(tickets.items()):
                writer.writerow([
                    ticket["ticket_id"],
                    ticket["name"],
                    ticket["email"],
                    ticket["short_description"],
                    ticket["status"],
                    ticket["timestamp"],
                    ticket["long_description"]
                ])
        append_log("* Ticket database saved.")
    except Exception as e:
        append_log(f"* | ERROR: Failed to save data: {e}")

#------------------------------------------------------------
# Ticket actions

def create_ticket(fields):
    """Create a new ticket"""
    global next_ticket_id
    if len(fields) < 3:
        return "ERROR | Invalid ticket creation format\n"

    name = fields[0].strip()
    email = fields[1].strip()
    short_description = fields[2].strip()

    if not name or not email or not short_description:
        return "ERROR | Missing ticket fields\n"

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
    if len(fields) < 2:
        return "ERROR | Invalid status check format\n"

    try:
        ticket_id = int(fields[0])
    except ValueError:
        return "ERROR | Invalid ticket ID format\n"

    email = fields[1].strip()

    if ticket_id not in tickets:
        return "ERROR | Ticket not found\n"

    ticket = tickets[ticket_id]
    if ticket["email"].lower() != email.lower():
        return "ERROR | Unauthorized access - email does not match ticket owner\n"

    return f"SUCCESS | STATUS | {ticket_id} | {ticket['status']} | {ticket['timestamp']} | {ticket['long_description']}\n"


def view_my_tickets(fields):
    """View all tickets for a specific customer email"""
    if len(fields) < 1:
        return "ERROR | Invalid view request format\n"

    email = fields[0].strip().lower()
    customer_tickets = []

    for ticket_id, ticket in sorted(tickets.items()):
        if ticket["email"].lower() == email:
            customer_tickets.append(f"{ticket['ticket_id']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']}")

    if not customer_tickets:
        return "SUCCESS | TICKET_LIST | No tickets found\n"

    ticket_list = " ; ".join(customer_tickets)
    return f"SUCCESS | TICKET_LIST | {ticket_list}\n"


def filter_my_tickets(fields):
    """Filter customer tickets by status"""
    if len(fields) < 2:
        return "ERROR | Invalid filter format\n"

    email = fields[0].strip().lower()
    status = fields[1].strip().lower()
    filtered_tickets = []

    for ticket_id, ticket in sorted(tickets.items()):
        if ticket["email"].lower() == email and ticket["status"].lower() == status:
            filtered_tickets.append(f"{ticket['ticket_id']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']}")

    if not filtered_tickets:
        return f"SUCCESS | FILTERED_LIST | No tickets with status '{status}' found\n"

    ticket_list = " ; ".join(filtered_tickets)
    return f"SUCCESS | FILTERED_LIST | {ticket_list}\n"


def admin_view_all():
    """View all tickets in database (admin only)"""
    all_tickets = []
    for ticket_id, ticket in sorted(tickets.items()):
        all_tickets.append(f"{ticket['ticket_id']} | {ticket['name']} | {ticket['email']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']} | {ticket['long_description']}")

    if not all_tickets:
        return "SUCCESS | TICKET_LIST | Database is empty\n"

    ticket_list = " ; ".join(all_tickets)
    return f"SUCCESS | TICKET_LIST | {ticket_list}\n"


def admin_filter_tickets(fields):
    """Filter all tickets by status (admin only)"""
    if len(fields) < 1:
        return "ERROR | Invalid filter format\n"

    status = fields[0].strip().lower()
    filtered_tickets = []

    for ticket_id, ticket in sorted(tickets.items()):
        if ticket["status"].lower() == status:
            filtered_tickets.append(f"{ticket['ticket_id']} | {ticket['name']} | {ticket['email']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']} | {ticket['long_description']}")

    if not filtered_tickets:
        return f"SUCCESS | FILTERED_LIST | No tickets with status '{status}' found\n"

    ticket_list = " ; ".join(filtered_tickets)
    return f"SUCCESS | FILTERED_LIST | {ticket_list}\n"


def admin_search_ticket(fields):
    """Search for specific ticket by ID (admin only)"""
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
    if len(fields) < 3:
        return "ERROR | Invalid update format\n"

    try:
        ticket_id = int(fields[0])
    except ValueError:
        return "ERROR | Invalid ticket ID format\n"

    if ticket_id not in tickets:
        return "ERROR | Ticket not found\n"

    new_status = fields[1].strip().lower()
    long_description = fields[2].strip()

    if new_status not in ["open", "closed", "in_progress", "pending"]:
        return "ERROR | Invalid status\n"

    tickets[ticket_id]["status"] = new_status
    tickets[ticket_id]["long_description"] = long_description

    save_data()
    return f"SUCCESS | TICKET_UPDATED | {ticket_id} | {new_status} | {long_description}\n"


def admin_view_by_name(fields):
    """View tickets filtered by customer name (admin only)"""
    if len(fields) < 1:
        return "ERROR | Invalid view format\n"

    customer_name = fields[0].strip().lower()
    matching_tickets = []

    for ticket_id, ticket in sorted(tickets.items()):
        if customer_name in ticket["name"].lower():
            matching_tickets.append(f"{ticket['ticket_id']} | {ticket['name']} | {ticket['email']} | {ticket['status']} | {ticket['timestamp']} | {ticket['short_description']} | {ticket['long_description']}")

    if not matching_tickets:
        return f"SUCCESS | TICKET_LIST | No tickets found for customer '{fields[0].strip()}'\n"

    ticket_list = " ; ".join(matching_tickets)
    return f"SUCCESS | TICKET_LIST | {ticket_list}\n"


def admin_view_by_id(fields):
    """View full details of ticket by ID (admin only)"""
    if len(fields) < 1:
        return "ERROR | Invalid view format\n"

    try:
        ticket_id = int(fields[0])
    except ValueError:
        return "ERROR | Invalid ticket ID format\n"

    if ticket_id not in tickets:
        return "ERROR | Ticket not found\n"

    ticket = tickets[ticket_id]
    ticket_data = (
        f"ticket_id: {ticket['ticket_id']} | name: {ticket['name']} | email: {ticket['email']} | "
        f"status: {ticket['status']} | timestamp: {ticket['timestamp']} | "
        f"short_description: {ticket['short_description']} | long_description: {ticket['long_description']}"
    )
    return f"SUCCESS | TICKET_FOUND | {ticket_data}\n"

#------------------------------------------------------------
# Server logging and GUI helpers

def append_log(message):
    global log_widget
    if log_widget is not None:
        def write():
            log_widget.configure(state='normal')
            log_widget.insert(tk.END, message + "\n")
            log_widget.see(tk.END)
            log_widget.configure(state='disabled')
        log_widget.after(0, write)
    else:
        print(message)


def set_status_label(label_widget, text):
    label_widget.after(0, lambda: label_widget.config(text=text))

#------------------------------------------------------------
# Client connection handler

def TicketThread(connectSocket):
    """Handle individual client connection"""
    append_log("* | Starting connection for service")
    admin_authenticated = False

    while True:
        try:
            clientRequest = connectSocket.recv(4096).decode()
            if not clientRequest:
                break

            append_log(f"* | Received: {clientRequest.strip()}")
            parts = [part.strip() for part in clientRequest.strip().split(" | ")]
            command = parts[0].upper()
            fields = parts[1:] if len(parts) > 1 else []
            response = ""

            if command == "ADMIN_LOGIN":
                if len(fields) >= 2:
                    username, password = fields[0], fields[1]
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
                response = admin_view_all() if admin_authenticated else "ERROR | Unauthorized - admin access required\n"
            elif command == "FILTER_TICKETS":
                response = admin_filter_tickets(fields) if admin_authenticated else "ERROR | Unauthorized - admin access required\n"
            elif command == "SEARCH_TICKET":
                response = admin_search_ticket(fields) if admin_authenticated else "ERROR | Unauthorized - admin access required\n"
            elif command == "UPDATE_TICKET":
                response = admin_update_ticket(fields) if admin_authenticated else "ERROR | Unauthorized - admin access required\n"
            elif command == "VIEW_BY_NAME":
                response = admin_view_by_name(fields) if admin_authenticated else "ERROR | Unauthorized - admin access required\n"
            elif command == "VIEW_BY_ID":
                response = admin_view_by_id(fields) if admin_authenticated else "ERROR | Unauthorized - admin access required\n"
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

            connectSocket.send(response.encode())
            append_log(f"* | Sent: {response.strip()}")
        except Exception as e:
            append_log(f"* | ERROR: {e}")
            try:
                connectSocket.send(f"ERROR | Server error: {str(e)}\n".encode())
            except Exception:
                pass
            break

    connectSocket.close()
    append_log("* | Connection closed")

#------------------------------------------------------------
# Server control and GUI

def accept_connections(host, port, status_label):
    global serverSocket, server_running
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serverSocket.bind((host, port))
        serverSocket.listen(5)
        serverSocket.settimeout(1)
        server_running = True
        append_log(f"* Server listening on {host}:{port}")
        set_status_label(status_label, f"Running on {host}:{port}")

        while server_running:
            try:
                clientSocket, clientAddr = serverSocket.accept()
                append_log(f"* | Client connected from {clientAddr}")
                start_new_thread(TicketThread, (clientSocket,))
            except timeout:
                continue
            except OSError:
                break
    except Exception as e:
        append_log(f"* | ERROR starting server: {e}")
        messagebox.showerror("Server Error", f"Could not start server: {e}")
    finally:
        server_running = False
        if serverSocket is not None:
            try:
                serverSocket.close()
            except Exception:
                pass
        set_status_label(status_label, "Stopped")
        append_log("* Server stopped")


def start_server(host_entry, port_entry, status_label, start_button, stop_button):
    global server_thread, host_value, port_value
    if server_running:
        return

    host = host_entry.get().strip() or "127.0.0.1"
    try:
        port = int(port_entry.get().strip())
    except ValueError:
        messagebox.showwarning("Invalid Port", "Port must be a number.")
        return

    host_value = host
    port_value = port
    data_dir = Path(__file__).parent / "Data"
    data_dir.mkdir(exist_ok=True)
    load_users()
    load_data()

    server_thread = threading.Thread(target=accept_connections, args=(host, port, status_label), daemon=True)
    server_thread.start()
    start_button.config(state='disabled')
    stop_button.config(state='normal')
    append_log("* | Server thread started")


def stop_server(start_button, stop_button):
    global server_running, serverSocket
    if not server_running:
        return
    server_running = False
    if serverSocket is not None:
        try:
            serverSocket.close()
        except Exception:
            pass
    start_button.config(state='normal')
    stop_button.config(state='disabled')
    append_log("* | Stop requested")


def build_gui():
    root = tk.Tk()
    root.title("Ticket Server GUI")
    root.geometry("800x520")

    mainframe = ttk.Frame(root, padding=12)
    mainframe.grid(row=0, column=0, sticky='NSEW')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    header = ttk.Label(mainframe, text="Ticket Server", font=("Segoe UI", 16, "bold"))
    header.grid(row=0, column=0, columnspan=4, pady=(0, 10))

    ttk.Label(mainframe, text="Host:").grid(row=1, column=0, sticky='E')
    host_entry = ttk.Entry(mainframe)
    host_entry.grid(row=1, column=1, sticky='WE', padx=(0, 10))
    host_entry.insert(0, host_value)

    ttk.Label(mainframe, text="Port:").grid(row=1, column=2, sticky='E')
    port_entry = ttk.Entry(mainframe)
    port_entry.grid(row=1, column=3, sticky='WE')
    port_entry.insert(0, str(port_value))

    status_label = ttk.Label(mainframe, text="Stopped", foreground='red')
    status_label.grid(row=2, column=0, columnspan=4, sticky='W', pady=(6, 10))

    start_button = ttk.Button(mainframe, text="Start Server", command=lambda: start_server(host_entry, port_entry, status_label, start_button, stop_button))
    start_button.grid(row=3, column=0, columnspan=2, sticky='WE', padx=(0, 10))
    stop_button = ttk.Button(mainframe, text="Stop Server", command=lambda: stop_server(start_button, stop_button), state='disabled')
    stop_button.grid(row=3, column=2, columnspan=2, sticky='WE')

    log_label = ttk.Label(mainframe, text="Server Log:")
    log_label.grid(row=4, column=0, columnspan=4, sticky='W', pady=(10, 0))

    global log_widget
    log_widget = scrolledtext.ScrolledText(mainframe, width=96, height=20, state='disabled')
    log_widget.grid(row=5, column=0, columnspan=4, sticky='NSEW', pady=(4, 0))

    mainframe.columnconfigure(1, weight=1)
    mainframe.columnconfigure(3, weight=1)
    mainframe.rowconfigure(5, weight=1)

    append_log("* Server GUI ready.")
    root.protocol("WM_DELETE_WINDOW", lambda: (stop_server(start_button, stop_button), root.destroy()))
    root.mainloop()

#------------------------------------------------------------
if __name__ == "__main__":
    build_gui()
