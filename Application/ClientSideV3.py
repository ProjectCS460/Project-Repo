#!/usr/bin/python3
# Ticket App Client V1
# AUTHOR: 	JacobT2006
# CREATED: 	04/9/2026
# VERSION 1: 	Handles connection to ServerSide and ready for client-side UI
# VERSION 2:

import socket, re, tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# --- ServiceNow UI Theme ---
COLOR_BG = "#161b22"      # Dark Sidebar
COLOR_MAIN = "#0d1117"    # Main Canvas
COLOR_ACCENT = "#58a6ff"  # ServiceNow Blue
COLOR_TEXT = "#c9d1d9"    # Primary Text
COLOR_INPUT = "#0d1117"   # Input fields
COLOR_CARD = "#21262d"    # Ticket Cards

class ServiceNowUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ServiceLater Portal - IT Service Management")
        self.root.geometry("1100x850")
        self.root.configure(bg=COLOR_MAIN)
        self.sock = None
        self.apply_styles()
        self.build_layout()

    def apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=COLOR_MAIN, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("Sidebar.TFrame", background=COLOR_BG)
        style.configure("Nav.TButton", background=COLOR_BG, foreground=COLOR_TEXT, borderwidth=0, padding=10, font=("Segoe UI", 11, "bold"))
        style.map("Nav.TButton", background=[("active", COLOR_ACCENT)])
        style.configure("Action.TButton", background=COLOR_ACCENT, foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground=COLOR_INPUT, foreground="white", borderwidth=1)
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background=COLOR_MAIN, foreground="white")

    def build_layout(self):
        # Sidebar
        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=200)
        self.sidebar.pack(side="left", fill="y")
        
        ttk.Label(self.sidebar, text="ServiceLater", font=("Segoe UI", 14, "bold"), background=COLOR_BG, foreground=COLOR_ACCENT).pack(pady=20)
        
        ttk.Button(self.sidebar, text="Self-Service", style="Nav.TButton", command=lambda: self.show_page(self.page_cust)).pack(fill="x")
        ttk.Button(self.sidebar, text="Admin Workspace", style="Nav.TButton", command=lambda: self.show_page(self.page_admin)).pack(fill="x")
        
        # Main Content Area
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        # Pages
        self.page_cust = ttk.Frame(self.main_container)
        self.page_admin = ttk.Frame(self.main_container)
        
        self.build_customer_page()
        self.build_admin_page()
        
        # Output Terminal (Activity Stream)
        ttk.Label(self.main_container, text="Activity Stream / Response:", font=("Segoe UI", 10, "italic")).pack(anchor="w")
        self.terminal = scrolledtext.ScrolledText(self.main_container, height=15, bg=COLOR_INPUT, fg="#7ee787", font=("Consolas", 10), borderwidth=0)
        self.terminal.pack(fill="both", expand=True, pady=(5, 0))
        
        self.show_page(self.page_cust)

    def show_page(self, page):
        for p in [self.page_cust, self.page_admin]: p.pack_forget()
        page.pack(fill="both", expand=True)

    # --- Customer View ---
    def build_customer_page(self):
        ttk.Label(self.page_cust, text="Incident Self-Service", style="Header.TLabel").pack(anchor="w", pady=10)
        
        form = ttk.LabelFrame(self.page_cust, text="Report a New Issue")
        form.pack(fill="x", pady=10)
        
        cols = ttk.Frame(form); cols.pack(fill="x", padx=10, pady=10)
        ttk.Label(cols, text="Your Name:").grid(row=0, column=0, sticky="w")
        self.c_name = ttk.Entry(cols, width=30); self.c_name.grid(row=0, column=1, padx=5)
        
        ttk.Label(cols, text="Contact Email:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.c_email = ttk.Entry(cols, width=30); self.c_email.grid(row=0, column=3, padx=5)
        
        ttk.Label(form, text="Short Description (Summary):").pack(anchor="w", padx=10)
        self.c_desc = ttk.Entry(form); self.c_desc.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(form, text="Submit Incident", style="Action.TButton", command=self.submit_incident).pack(pady=10)

        view_bar = ttk.LabelFrame(self.page_cust, text="Check My Incidents(Email)")
        view_bar.pack(fill="x", pady=10)
        self.v_email = ttk.Entry(view_bar, width=40); self.v_email.pack(side="left", padx=10, pady=10)
        ttk.Button(view_bar, text="Search My History", command=self.view_my_incidents).pack(side="left", padx=5)

    # --- Admin View ---
    def build_admin_page(self):
        self.admin_login_f = ttk.Frame(self.page_admin)
        self.admin_login_f.pack(expand=True)
        
        ttk.Label(self.admin_login_f, text="Admin Login", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        # Username field
        user_frame = ttk.Frame(self.admin_login_f)
        user_frame.pack(pady=5)
        ttk.Label(user_frame, text="Username:").pack(side="left", padx=(0, 5))
        self.a_user = ttk.Entry(user_frame)
        self.a_user.pack(side="left")
        
        # Password field
        pass_frame = ttk.Frame(self.admin_login_f)
        pass_frame.pack(pady=5)
        ttk.Label(pass_frame, text="Password:").pack(side="left", padx=(0, 5))
        self.a_pass = ttk.Entry(pass_frame, show="*")
        self.a_pass.pack(side="left")
        
        ttk.Button(self.admin_login_f, text="Authenticate", command=self.admin_login).pack(pady=10)

        self.admin_work_f = ttk.Frame(self.page_admin)
        
        # Tools Bar
        tools = ttk.LabelFrame(self.admin_work_f, text="Global Incident Controls")
        tools.pack(fill="x", pady=5)
        ttk.Button(tools, text="All Incidents", command=lambda: self.send_req("ADMIN_QUERY|ALL")).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Label(tools, text="Filter Status:").grid(row=0, column=1)
        self.f_stat = ttk.Combobox(tools, values=["open", "in_progress", "closed", "pending"], width=10)
        self.f_stat.grid(row=0, column=2, padx=5)
        ttk.Button(tools, text="Filter", command=lambda: self.send_req(f"ADMIN_QUERY|STATUS|{self.f_stat.get()}")).grid(row=0, column=3)
        
        ttk.Label(tools, text="Search ID:").grid(row=0, column=4, padx=(20, 0))
        self.f_id = ttk.Entry(tools, width=10); self.f_id.grid(row=0, column=5)
        ttk.Button(tools, text="Go", command=lambda: self.send_req(f"ADMIN_QUERY|ID|{self.f_id.get()}")).grid(row=0, column=6, padx=5)
        
        ttk.Button(tools, text="Logout", command=self.admin_logout).grid(row=0, column=7, padx=(50, 0))

        # Update Bar
        upd = ttk.LabelFrame(self.admin_work_f, text="Resolution & Updates")
        upd.pack(fill="x", pady=10)
        ttk.Label(upd, text="ID:").grid(row=0, column=0, padx=5)
        self.u_id = ttk.Entry(upd, width=8); self.u_id.grid(row=0, column=1)
        ttk.Label(upd, text="State:").grid(row=0, column=2, padx=5)
        self.u_stat = ttk.Combobox(upd, values=["open", "in_progress", "closed", "pending"], width=12); self.u_stat.grid(row=0, column=3)
        ttk.Label(upd, text="Journal Note:").grid(row=0, column=4, padx=5)
        self.u_note = ttk.Entry(upd, width=40); self.u_note.grid(row=0, column=5, padx=5)
        ttk.Button(upd, text="Post Update", style="Action.TButton", command=self.admin_update).grid(row=0, column=6, padx=5, pady=10)

    # --- Networking ---
    def get_conn(self):
        if not self.sock:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(("10.0.2.15", 13000))
                return True
            except: messagebox.showerror("System", "ServiceNow Backend is unreachable."); return False
        return True

    def send_req(self, msg):
        if self.get_conn():
            try:
                self.sock.sendall((msg + "\n").encode())
                resp = self.sock.recv(16384).decode().strip()
                self.handle_resp(resp)
            except: self.sock = None

    def handle_resp(self, resp):
        self.terminal.configure(state='normal')
        self.terminal.delete("1.0", tk.END)
        parts = resp.split("|")
        
        if parts[0].strip() == "SUCCESS":
            if "LIST" in parts[1]:
                data = parts[2].split(" ; ")
                for d in data: self.terminal.insert(tk.END, d.replace("\\n", "\n") + "\n")
            else: self.terminal.insert(tk.END, f">>> {parts[2]}")
        else:
            self.terminal.insert(tk.END, f"!!! SERVER ERROR: {resp}")
        self.terminal.configure(state='disabled')

    # --- Logic ---
    def submit_incident(self):
        email = self.c_email.get().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showwarning("Validation", "Please provide a valid contact email."); return
        self.send_req(f"CREATE_TICKET|{self.c_name.get()}|{email}|{self.c_desc.get()}")
        self.sock.close(); self.sock = None # Customer sessions are transactional

    def view_my_incidents(self):
        self.send_req(f"VIEW_MY_TICKETS|{self.v_email.get()}")
        if self.sock: self.sock.close(); self.sock = None

    def admin_login(self):
        self.send_req(f"LOGIN|{self.a_user.get()}|{self.a_pass.get()}")
        if self.sock: 
            self.admin_login_f.pack_forget()
            self.admin_work_f.pack(fill="both", expand=True)

    def admin_update(self):
        if not self.u_id.get() or not self.u_note.get():
            messagebox.showwarning("Validation", "Incident ID and Journal Note are required."); return
        self.send_req(f"UPDATE_TICKET|{self.u_id.get()}|{self.u_stat.get()}|{self.u_note.get()}")

    def admin_logout(self):
        self.send_req("LOGOUT")
        self.sock.close(); self.sock = None
        self.admin_work_f.pack_forget(); self.admin_login_f.pack(expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceNowUI(root)
    root.mainloop()
