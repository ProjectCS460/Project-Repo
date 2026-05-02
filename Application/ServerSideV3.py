#!/usr/bin/python3
# Ticket App Server V2
# AUTHOR: 	JacobT2006
# CREATED: 	04/9/2026
# VERSION 1: 	Handles input from ClientSide and ticket data as well as login validation
# VERSION 2: 	Added GUI and logging, improved error handling and added more admin features
# VERSION 3:    Closed inputs and made static

import socket, threading, csv, os
from datetime import datetime

# --- Configuration ---
HOST, PORT = "10.0.2.15", 13000
DATA_DIR = "Data"
TICKET_FILE = os.path.join(DATA_DIR, "DATA.csv")
LOGIN_FILE = os.path.join(DATA_DIR, "LOGIN.csv")
db_lock = threading.Lock()

# --- Database Management ---
tickets = {}
users = {}

def load_data():
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    with db_lock:
        if os.path.exists(LOGIN_FILE):
            with open(LOGIN_FILE, 'r') as f:
                for r in csv.reader(f):
                    if len(r) >= 3: users[r[0].strip()] = (r[1].strip(), r[2].strip().lower())
        if os.path.exists(TICKET_FILE):
            with open(TICKET_FILE, 'r') as f:
                for r in csv.DictReader(f): tickets[int(r['ticket_id'])] = r
    print(f"[*] Loaded {len(users)} users and {len(tickets)} tickets.")

def save_tickets():
    with db_lock:
        with open(TICKET_FILE, 'w', newline='') as f:
            fieldnames = ["ticket_id", "name", "email", "short_description", "status", "timestamp", "long_description"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for tid in sorted(tickets.keys()): writer.writerow(tickets[tid])

def format_ticket(t):
    """Creates a ServiceNow 'Activity Stream' look for each ticket."""
    return (f"Number: INC{t['ticket_id']}\\n"
            f"State: {t['status'].upper()}\\n"
            f"Caller: {t['name']} ({t['email']})\\n"
            f"Short Description: {t['short_description']}\\n"
            f"Activity Log: {t.get('long_description', 'No entries')}\\n"
            f"{'='*50}")

# --- Command Logic ---
def handle_client(conn, addr):
    is_admin = False
    session_user = ""
    print(f"[+] New Connection: {addr}")
    
    try:
        while True:
            raw_data = conn.recv(8192).decode().strip()
            if not raw_data: break
            
            parts = [p.strip() for p in raw_data.split("|")]
            cmd = parts[0]
            resp = "ERROR | Invalid Request"

            if cmd == "LOGIN":
                user, pw = parts[1], parts[2]
                if user in users and users[user][0] == pw and users[user][1] == "admin":
                    is_admin, session_user = True, user
                    resp = f"SUCCESS | AUTH | Welcome, {user}"
                else: resp = "ERROR | Invalid Credentials"

            elif cmd == "LOGOUT":
                is_admin = False
                resp = "SUCCESS | LOGOUT | Session Terminated"

            elif cmd == "CREATE_TICKET":
                new_id = max(tickets.keys() or [1000]) + 1
                tickets[new_id] = {
                    "ticket_id": str(new_id), "name": parts[1], "email": parts[2],
                    "short_description": parts[3], "status": "open",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "long_description": ""
                }
                save_tickets()
                resp = f"SUCCESS | CREATED | INC{new_id} generated."

            elif cmd == "VIEW_MY_TICKETS":
                email = parts[1].lower()
                matches = [format_ticket(t) for t in tickets.values() if t['email'].lower() == email]
                resp = f"SUCCESS | LIST | {' ; '.join(matches)}" if matches else "SUCCESS | LIST | No incidents found."

            elif cmd == "ADMIN_QUERY":
                if not is_admin: resp = "ERROR | Unauthorized"
                else:
                    query_type = parts[1] # ALL, STATUS, NAME, ID
                    val = parts[2] if len(parts) > 2 else ""
                    
                    if query_type == "ALL":
                        res = [format_ticket(t) for t in tickets.values()]
                    elif query_type == "STATUS":
                        res = [format_ticket(t) for t in tickets.values() if t['status'] == val]
                    elif query_type == "NAME":
                        res = [format_ticket(t) for t in tickets.values() if val.lower() in t['name'].lower()]
                    elif query_type == "ID":
                        tid = int(val.replace("INC", "")) if val.replace("INC", "").isdigit() else 0
                        res = [format_ticket(tickets[tid])] if tid in tickets else []
                    
                    resp = f"SUCCESS | LIST | {' ; '.join(res)}" if res else "SUCCESS | LIST | No records match."

            elif cmd == "UPDATE_TICKET":
                if not is_admin: resp = "ERROR | Unauthorized"
                else:
                    tid = int(parts[1].replace("INC", ""))
                    if tid in tickets:
                        tickets[tid]['status'] = parts[2]
                        entry = f"[{datetime.now().strftime('%m-%d %H:%M')}] ({session_user}): {parts[3]}"
                        tickets[tid]['long_description'] += f" | {entry}" if tickets[tid]['long_description'] else entry
                        save_tickets()
                        resp = f"SUCCESS | UPDATED | INC{tid} updated successfully."
                    else: resp = "ERROR | Incident not found."

            conn.sendall((resp + "\n").encode())
    except Exception as e: print(f"[!] Error: {e}")
    finally: conn.close(); print(f"[-] Disconnected: {addr}")

# --- Start Server ---
load_data()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT)); server.listen(10)
print(f"[*] ServiceNow Backend running on {HOST}:{PORT}")
while True:
    client_conn, client_addr = server.accept()
    threading.Thread(target=handle_client, args=(client_conn, client_addr), daemon=True).start()
