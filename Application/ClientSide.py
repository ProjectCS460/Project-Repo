#!/usr/bin/python3
# Ticket App Client V1
# VERSION 1: 	Handles connection to ServerSide and ready for client-side UI
# AUTHOR: 	JacobT2006
# CREATED: 	04/9/2026

import sys
import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class TicketClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ticket Client GUI")
        self.root.geometry("900x660")
        self.server_socket = None
        self.admin_authenticated = False

        self.host_var = tk.StringVar(value="10.0.2.15")
        self.port_var = tk.StringVar(value="13000")
        self.status_var = tk.StringVar(value="Not connected")

        self.build_gui()

    def build_gui(self):
        mainframe = ttk.Frame(self.root, padding=12)
        mainframe.grid(row=0, column=0, sticky='NSEW')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        header = ttk.Label(mainframe, text="Ticket Client", font=("Segoe UI", 18, "bold"))
        header.grid(row=0, column=0, columnspan=4, pady=(0, 12))

        ttk.Label(mainframe, text="Server Host:").grid(row=1, column=0, sticky='E')
        host_entry = ttk.Entry(mainframe, textvariable=self.host_var)
        host_entry.grid(row=1, column=1, sticky='WE', padx=(0, 10))

        ttk.Label(mainframe, text="Server Port:").grid(row=1, column=2, sticky='E')
        port_entry = ttk.Entry(mainframe, textvariable=self.port_var)
        port_entry.grid(row=1, column=3, sticky='WE')

        connect_button = ttk.Button(mainframe, text="Connect", command=self.connect_to_server)
        connect_button.grid(row=2, column=0, columnspan=2, sticky='WE', pady=(8, 0), padx=(0, 10))
        disconnect_button = ttk.Button(mainframe, text="Disconnect", command=self.disconnect_from_server)
        disconnect_button.grid(row=2, column=2, columnspan=2, sticky='WE', pady=(8, 0))

        ttk.Label(mainframe, textvariable=self.status_var, foreground='blue').grid(row=3, column=0, columnspan=4, sticky='W', pady=(8, 12))

        self.notebook = ttk.Notebook(mainframe)
        self.notebook.grid(row=4, column=0, columnspan=4, sticky='NSEW')

        self.build_customer_tab()
        self.build_admin_tab()

        self.response_box = scrolledtext.ScrolledText(mainframe, width=108, height=16, state='disabled')
        self.response_box.grid(row=5, column=0, columnspan=4, sticky='NSEW', pady=(12, 0))

        mainframe.columnconfigure(1, weight=1)
        mainframe.columnconfigure(3, weight=1)
        mainframe.rowconfigure(5, weight=1)

        self.update_ui_state(False)
        self.log_response("Client GUI ready.")

    def build_customer_tab(self):
        customer_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(customer_frame, text="Customer")

        ttk.Label(customer_frame, text="Create Ticket", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=4, sticky='W')
        ttk.Label(customer_frame, text="Name:").grid(row=1, column=0, sticky='E')
        self.name_entry = ttk.Entry(customer_frame, width=28)
        self.name_entry.grid(row=1, column=1, sticky='WE', padx=(0, 10))
        ttk.Label(customer_frame, text="Email:").grid(row=1, column=2, sticky='E')
        self.email_entry = ttk.Entry(customer_frame, width=28)
        self.email_entry.grid(row=1, column=3, sticky='WE')

        ttk.Label(customer_frame, text="Short Description:").grid(row=2, column=0, sticky='NE', pady=(8, 0))
        self.short_desc = tk.Text(customer_frame, width=68, height=4, wrap='word')
        self.short_desc.grid(row=2, column=1, columnspan=3, sticky='WE', pady=(8, 0))
        ttk.Button(customer_frame, text="Create Ticket", command=self.create_ticket).grid(row=3, column=3, sticky='E', pady=(8, 0))

        ttk.Separator(customer_frame, orient='horizontal').grid(row=4, column=0, columnspan=4, sticky='EW', pady=12)

        ttk.Label(customer_frame, text="View My Tickets", font=("Segoe UI", 12, "bold")).grid(row=5, column=0, columnspan=4, sticky='W')
        ttk.Label(customer_frame, text="Email:").grid(row=6, column=0, sticky='E')
        self.view_email_entry = ttk.Entry(customer_frame, width=28)
        self.view_email_entry.grid(row=6, column=1, sticky='WE', padx=(0, 10))
        ttk.Button(customer_frame, text="View Tickets", command=self.view_my_tickets).grid(row=6, column=3, sticky='E')

        ttk.Label(customer_frame, text="Filter Status:").grid(row=7, column=0, sticky='E', pady=(8, 0))
        self.filter_status_var = tk.StringVar(value="open")
        self.filter_status = ttk.Combobox(customer_frame, textvariable=self.filter_status_var, values=["open", "closed", "in_progress", "pending"], state='readonly', width=26)
        self.filter_status.grid(row=7, column=1, sticky='WE', padx=(0, 10), pady=(8, 0))
        ttk.Button(customer_frame, text="Filter My Tickets", command=self.filter_my_tickets).grid(row=7, column=3, sticky='E', pady=(8, 0))

        ttk.Label(customer_frame, text="Check Status", font=("Segoe UI", 12, "bold")).grid(row=8, column=0, columnspan=4, sticky='W', pady=(16, 0))
        ttk.Label(customer_frame, text="Ticket ID:").grid(row=9, column=0, sticky='E')
        self.status_ticket_entry = ttk.Entry(customer_frame, width=28)
        self.status_ticket_entry.grid(row=9, column=1, sticky='WE', padx=(0, 10))
        ttk.Label(customer_frame, text="Email:").grid(row=9, column=2, sticky='E')
        self.status_email_entry = ttk.Entry(customer_frame, width=28)
        self.status_email_entry.grid(row=9, column=3, sticky='WE')
        ttk.Button(customer_frame, text="Check Status", command=self.check_status).grid(row=10, column=3, sticky='E', pady=(8, 0))

        for idx in range(4):
            customer_frame.columnconfigure(idx, weight=1)

    def build_admin_tab(self):
        admin_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(admin_frame, text="Admin")

        ttk.Label(admin_frame, text="Admin Login", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=4, sticky='W')
        ttk.Label(admin_frame, text="Username:").grid(row=1, column=0, sticky='E')
        self.admin_user_entry = ttk.Entry(admin_frame, width=28)
        self.admin_user_entry.grid(row=1, column=1, sticky='WE', padx=(0, 10))
        ttk.Label(admin_frame, text="Password:").grid(row=1, column=2, sticky='E')
        self.admin_pass_entry = ttk.Entry(admin_frame, show='*', width=28)
        self.admin_pass_entry.grid(row=1, column=3, sticky='WE')
        ttk.Button(admin_frame, text="Login", command=self.admin_login).grid(row=2, column=3, sticky='E', pady=(8, 0))

        ttk.Separator(admin_frame, orient='horizontal').grid(row=3, column=0, columnspan=4, sticky='EW', pady=12)

        ttk.Button(admin_frame, text="View All Tickets", command=self.admin_view_all).grid(row=4, column=0, sticky='WE')
        ttk.Button(admin_frame, text="Logout", command=self.admin_logout).grid(row=4, column=1, sticky='WE', padx=(10, 0))

        ttk.Label(admin_frame, text="Ticket ID:").grid(row=5, column=0, sticky='E', pady=(12, 0))
        self.admin_ticket_id_entry = ttk.Entry(admin_frame, width=28)
        self.admin_ticket_id_entry.grid(row=5, column=1, sticky='WE', padx=(0, 10), pady=(12, 0))
        ttk.Button(admin_frame, text="Search Ticket", command=self.admin_search_ticket).grid(row=5, column=3, sticky='E', pady=(12, 0))

        ttk.Label(admin_frame, text="Filter Status:").grid(row=6, column=0, sticky='E', pady=(8, 0))
        self.admin_filter_status_var = tk.StringVar(value="open")
        self.admin_filter_status = ttk.Combobox(admin_frame, textvariable=self.admin_filter_status_var, values=["open", "closed", "in_progress", "pending"], state='readonly', width=26)
        self.admin_filter_status.grid(row=6, column=1, sticky='WE', padx=(0, 10), pady=(8, 0))
        ttk.Button(admin_frame, text="Filter Tickets", command=self.admin_filter_tickets).grid(row=6, column=3, sticky='E', pady=(8, 0))

        ttk.Label(admin_frame, text="View By Customer Name:").grid(row=7, column=0, sticky='E', pady=(8, 0))
        self.admin_view_name_entry = ttk.Entry(admin_frame, width=28)
        self.admin_view_name_entry.grid(row=7, column=1, sticky='WE', padx=(0, 10), pady=(8, 0))
        ttk.Button(admin_frame, text="View by Name", command=self.admin_view_by_name).grid(row=7, column=3, sticky='E', pady=(8, 0))

        ttk.Label(admin_frame, text="View By ID:").grid(row=8, column=0, sticky='E', pady=(8, 0))
        self.admin_view_id_entry = ttk.Entry(admin_frame, width=28)
        self.admin_view_id_entry.grid(row=8, column=1, sticky='WE', padx=(0, 10), pady=(8, 0))
        ttk.Button(admin_frame, text="View by ID", command=self.admin_view_by_id).grid(row=8, column=3, sticky='E', pady=(8, 0))

        ttk.Separator(admin_frame, orient='horizontal').grid(row=9, column=0, columnspan=4, sticky='EW', pady=12)

        ttk.Label(admin_frame, text="Admin Create Ticket", font=("Segoe UI", 12, "bold")).grid(row=10, column=0, columnspan=4, sticky='W')
        ttk.Label(admin_frame, text="Name:").grid(row=11, column=0, sticky='E')
        self.admin_name_entry = ttk.Entry(admin_frame, width=28)
        self.admin_name_entry.grid(row=11, column=1, sticky='WE', padx=(0, 10))
        ttk.Label(admin_frame, text="Email:").grid(row=11, column=2, sticky='E')
        self.admin_email_entry = ttk.Entry(admin_frame, width=28)
        self.admin_email_entry.grid(row=11, column=3, sticky='WE')

        ttk.Label(admin_frame, text="Short Description:").grid(row=12, column=0, sticky='NE', pady=(8, 0))
        self.admin_short_desc = tk.Text(admin_frame, width=68, height=3, wrap='word')
        self.admin_short_desc.grid(row=12, column=1, columnspan=3, sticky='WE', pady=(8, 0))
        ttk.Button(admin_frame, text="Create Ticket", command=self.admin_create_ticket).grid(row=13, column=3, sticky='E', pady=(8, 0))

        ttk.Separator(admin_frame, orient='horizontal').grid(row=14, column=0, columnspan=4, sticky='EW', pady=12)

        ttk.Label(admin_frame, text="Update Ticket", font=("Segoe UI", 12, "bold")).grid(row=15, column=0, columnspan=4, sticky='W')
        ttk.Label(admin_frame, text="Ticket ID:").grid(row=16, column=0, sticky='E')
        self.update_ticket_id_entry = ttk.Entry(admin_frame, width=28)
        self.update_ticket_id_entry.grid(row=16, column=1, sticky='WE', padx=(0, 10))

        ttk.Label(admin_frame, text="New Status:").grid(row=16, column=2, sticky='E')
        self.update_status_var = tk.StringVar(value="open")
        self.update_status = ttk.Combobox(admin_frame, textvariable=self.update_status_var, values=["open", "closed", "in_progress", "pending"], state='readonly', width=26)
        self.update_status.grid(row=16, column=3, sticky='WE')

        ttk.Label(admin_frame, text="Long Description:").grid(row=17, column=0, sticky='NE', pady=(8, 0))
        self.update_long_desc = tk.Text(admin_frame, width=68, height=4, wrap='word')
        self.update_long_desc.grid(row=17, column=1, columnspan=3, sticky='WE', pady=(8, 0))
        ttk.Button(admin_frame, text="Update Ticket", command=self.admin_update_ticket).grid(row=18, column=3, sticky='E', pady=(8, 0))

        for idx in range(4):
            admin_frame.columnconfigure(idx, weight=1)

    def update_ui_state(self, connected):
        self.status_var.set("Connected" if connected else "Not connected")
        state = 'normal' if connected else 'disabled'
        for widget in [self.name_entry, self.email_entry, self.short_desc, self.view_email_entry, self.filter_status,
                       self.status_ticket_entry, self.status_email_entry, self.admin_user_entry, self.admin_pass_entry,
                       self.admin_ticket_id_entry, self.admin_filter_status, self.admin_view_name_entry,
                       self.admin_view_id_entry, self.admin_name_entry, self.admin_email_entry,
                       self.admin_short_desc, self.update_ticket_id_entry, self.update_status, self.update_long_desc]:
            try:
                widget.configure(state=state)
            except Exception:
                pass
        if not connected:
            self.admin_authenticated = False

    def connect_to_server(self):
        if self.server_socket is not None:
            self.log_response("Already connected to server.")
            return
        host = self.host_var.get().strip()
        try:
            port = int(self.port_var.get().strip())
        except ValueError:
            messagebox.showwarning("Invalid Port", "Port must be a number.")
            return
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.settimeout(5)
            self.server_socket.connect((host, port))
            self.log_response(f"Connected to server {host}:{port}")
            self.update_ui_state(True)
        except (ConnectionRefusedError, TimeoutError):
            self.log_response("ERROR: Could not connect to server. Check host, port, and server status.")
            self.server_socket = None
            self.update_ui_state(False)
        except Exception as e:
            self.log_response(f"ERROR: Connection failed - {e}")
            self.server_socket = None
            self.update_ui_state(False)

    def send_request(self, message):
        if self.server_socket is None:
            self.log_response("ERROR: Not connected to server.")
            return None
        try:
            self.server_socket.sendall((message.strip() + "\n").encode())
            self.log_response(f"Sent: {message}")
            return True
        except Exception as e:
            self.log_response(f"ERROR: Failed to send message - {e}")
            return None

    def receive_response(self):
        if self.server_socket is None:
            return None
        try:
            response = self.server_socket.recv(4096).decode()
            if response:
                self.log_response(f"Received: {response.strip()}")
                return response.strip()
            self.log_response("ERROR: Server closed connection.")
            return None
        except socket.timeout:
            self.log_response("ERROR: Server response timed out.")
            return None
        except Exception as e:
            self.log_response(f"ERROR: Failed to receive message - {e}")
            return None

    def disconnect_from_server(self):
        if self.server_socket is None:
            self.log_response("Not connected to server.")
            return
        self.send_request("DISCONNECT")
        self.receive_response()
        try:
            self.server_socket.close()
        except Exception:
            pass
        self.server_socket = None
        self.update_ui_state(False)
        self.log_response("Disconnected from server.")

    def process_response(self, response):
        if not response:
            return "No response returned."
        parts = [part.strip() for part in response.split(" | ")]
        if parts[0] == "ERROR":
            return "ERROR: " + " | ".join(parts[1:])
        if parts[0] == "SUCCESS":
            if len(parts) == 1:
                return "SUCCESS"
            if parts[1] == "TICKET_CREATED":
                return f"Ticket created successfully. Ticket ID: {parts[2]}"
            if parts[1] in ["TICKET_LIST", "FILTERED_LIST"]:
                return "Ticket list:\n" + parts[2]
            if parts[1] == "STATUS":
                return f"Ticket {parts[2]} status: {parts[3]}\nTimestamp: {parts[4]}\nNotes: {parts[5]}"
            if parts[1] == "ADMIN_AUTHENTICATED":
                self.admin_authenticated = True
                return "Admin login successful."
            if parts[1] == "TICKET_UPDATED":
                return f"Ticket {parts[2]} updated to {parts[3]}. Notes: {parts[4]}"
            if parts[1] == "TICKET_FOUND":
                return f"Ticket found:\n{parts[2]}"
            if parts[1] == "DISCONNECTED":
                return "Server acknowledged disconnect."
            return "SUCCESS: " + " | ".join(parts[1:])
        return response

    def log_response(self, message):
        self.response_box.configure(state='normal')
        self.response_box.insert(tk.END, message + "\n")
        self.response_box.see(tk.END)
        self.response_box.configure(state='disabled')

    def create_ticket(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        short_description = self.short_desc.get("1.0", tk.END).strip()
        if not name or not email or not short_description:
            messagebox.showwarning("Missing Fields", "Please provide name, email, and short description.")
            return
        if self.send_request(f"CREATE_TICKET | {name} | {email} | {short_description}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def view_my_tickets(self):
        email = self.view_email_entry.get().strip()
        if not email:
            messagebox.showwarning("Missing Email", "Please provide an email to view tickets.")
            return
        if self.send_request(f"VIEW_MY_TICKETS | {email}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def filter_my_tickets(self):
        email = self.view_email_entry.get().strip()
        status = self.filter_status_var.get().strip()
        if not email or not status:
            messagebox.showwarning("Missing Information", "Please provide email and status to filter.")
            return
        if self.send_request(f"FILTER_MY_TICKETS | {email} | {status}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def check_status(self):
        ticket_id = self.status_ticket_entry.get().strip()
        email = self.status_email_entry.get().strip()
        if not ticket_id or not email:
            messagebox.showwarning("Missing Information", "Please provide ticket ID and email.")
            return
        if self.send_request(f"CHECK_STATUS | {ticket_id} | {email}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def admin_login(self):
        username = self.admin_user_entry.get().strip()
        password = self.admin_pass_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing Credentials", "Enter admin username and password.")
            return
        if self.send_request(f"ADMIN_LOGIN | {username} | {password}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def admin_logout(self):
        if self.server_socket is None:
            self.log_response("ERROR: Not connected to server.")
            return
        if self.send_request("ADMIN_LOGOUT"):
            response = self.receive_response()
            self.admin_authenticated = False
            self.log_response(self.process_response(response))

    def admin_view_all(self):
        if not self.admin_authenticated:
            messagebox.showwarning("Unauthorized", "Please login as admin first.")
            return
        if self.send_request("VIEW_ALL_TICKETS"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def admin_filter_tickets(self):
        if not self.admin_authenticated:
            messagebox.showwarning("Unauthorized", "Please login as admin first.")
            return
        status = self.admin_filter_status_var.get().strip()
        if not status:
            messagebox.showwarning("Missing Status", "Choose a status to filter tickets.")
            return
        if self.send_request(f"FILTER_TICKETS | {status}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def admin_search_ticket(self):
        if not self.admin_authenticated:
            messagebox.showwarning("Unauthorized", "Please login as admin first.")
            return
        ticket_id = self.admin_ticket_id_entry.get().strip()
        if not ticket_id:
            messagebox.showwarning("Missing Ticket ID", "Enter a ticket ID to search.")
            return
        if self.send_request(f"SEARCH_TICKET | {ticket_id}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def admin_create_ticket(self):
        if not self.admin_authenticated:
            messagebox.showwarning("Unauthorized", "Please login as admin first.")
            return
        name = self.admin_name_entry.get().strip()
        email = self.admin_email_entry.get().strip()
        short_description = self.admin_short_desc.get("1.0", tk.END).strip()
        if not name or not email or not short_description:
            messagebox.showwarning("Missing Fields", "Please provide name, email, and short description.")
            return
        if self.send_request(f"CREATE_TICKET | {name} | {email} | {short_description}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def admin_view_by_name(self):
        if not self.admin_authenticated:
            messagebox.showwarning("Unauthorized", "Please login as admin first.")
            return
        name = self.admin_view_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Enter a customer name to search.")
            return
        if self.send_request(f"VIEW_BY_NAME | {name}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def admin_view_by_id(self):
        if not self.admin_authenticated:
            messagebox.showwarning("Unauthorized", "Please login as admin first.")
            return
        ticket_id = self.admin_view_id_entry.get().strip()
        if not ticket_id:
            messagebox.showwarning("Missing Ticket ID", "Enter a ticket ID to view.")
            return
        if self.send_request(f"VIEW_BY_ID | {ticket_id}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

    def admin_update_ticket(self):
        if not self.admin_authenticated:
            messagebox.showwarning("Unauthorized", "Please login as admin first.")
            return
        ticket_id = self.update_ticket_id_entry.get().strip()
        status = self.update_status_var.get().strip()
        long_description = self.update_long_desc.get("1.0", tk.END).strip()
        if not ticket_id or not status or not long_description:
            messagebox.showwarning("Missing Fields", "Enter ticket ID, status, and long description.")
            return
        if self.send_request(f"UPDATE_TICKET | {ticket_id} | {status} | {long_description}"):
            response = self.receive_response()
            self.log_response(self.process_response(response))

if __name__ == "__main__":
    root = tk.Tk()
    app = TicketClientApp(root)
    root.mainloop()
