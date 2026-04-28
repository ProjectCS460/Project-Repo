# Integration Guide - Ticket System Architecture

## Overview
The ticket system is now fully integrated with three layers:
- **ServerSide.py**: Socket server managing ticket database
- **TicketAPI.py**: Clean API layer for calling ticket functions
- **ClientSide.py**: CLI demonstration of how to use the API

## Data Flow
```
HTML Frontend
    ↓
TicketAPI.py (API functions)
    ↓
ClientSide.py (or direct socket communication)
    ↓
ServerSide.py (Socket server)
    ↓
Data/CSV files
```

## Setup & Running

### 1. Start the Server
```bash
cd Application
python3 ServerSide.py
```

Expected output:
```
* User database loaded.
* Ticket database loaded.
* Server listening on 127.0.0.1:13000
* | Waiting for client connection...
```

### 2. Test with CLI Client
```bash
cd Application
python3 ClientSide.py
```

This provides an interactive menu to test all functions.

### 3. Use TicketAPI for HTML Frontend

Import and use TicketAPI in your HTML application:

```python
# Example: Create a simple endpoint in Flask
from TicketAPI import *

@app.route('/api/create-ticket', methods=['POST'])
def create_ticket_endpoint():
    data = request.json
    success, ticket_id, msg = create_ticket(
        data['name'], 
        data['email'], 
        data['description']
    )
    return jsonify({"success": success, "ticket_id": ticket_id, "message": msg})
```

## API Functions Reference

### Connection Management
- `connect(host="127.0.0.1", port=13000)` → (success, message)
- `disconnect()` → (success, message)
- `is_connected()` → bool
- `is_admin_authenticated()` → bool

### Customer Functions
- `create_ticket(name, email, description)` → (success, ticket_id, message)
- `view_my_tickets(email)` → (success, tickets_data, message)
- `check_ticket_status(ticket_id, email)` → (success, data, message)
- `filter_my_tickets(email, status)` → (success, tickets_data, message)

### Admin Functions (require login)
- `admin_login(username, password)` → (success, message)
- `admin_logout()` → (success, message)
- `view_all_tickets()` → (success, tickets_data, message)
- `filter_tickets(status)` → (success, tickets_data, message)
- `search_ticket(ticket_id)` → (success, ticket_data, message)
- `update_ticket(ticket_id, new_status, description)` → (success, message)
- `view_by_name(customer_name)` → (success, tickets_data, message)
- `view_by_id(ticket_id)` → (success, ticket_data, message)

## Return Value Pattern

All API functions return tuples:

**Success case:**
```python
(True, data, "Success message")  # for functions with data
(True, "Success message")         # for functions without data
```

**Error case:**
```python
(False, None, "Error message")   # for functions with data
(False, "Error message")          # for functions without data
```

## Protocol Specification

All client-server communication uses this format:
```
CLIENT → SERVER: COMMAND | field1 | field2 | ... \n
SERVER → CLIENT: SUCCESS | data \n  or  ERROR | message \n
```

### Customer Commands
| Command | Format | Example |
|---------|--------|---------|
| Create Ticket | `CREATE_TICKET \| name \| email \| description` | `CREATE_TICKET \| John \| john@email.com \| Login issue` |
| View My Tickets | `VIEW_MY_TICKETS \| email` | `VIEW_MY_TICKETS \| john@email.com` |
| Check Status | `CHECK_STATUS \| ticket_id \| email` | `CHECK_STATUS \| 1001 \| john@email.com` |
| Filter My Tickets | `FILTER_MY_TICKETS \| email \| status` | `FILTER_MY_TICKETS \| john@email.com \| open` |

### Admin Commands
| Command | Format | Example |
|---------|--------|---------|
| Admin Login | `ADMIN_LOGIN \| username \| password` | `ADMIN_LOGIN \| admin \| password123` |
| View All | `VIEW_ALL_TICKETS` | `VIEW_ALL_TICKETS` |
| Filter Tickets | `FILTER_TICKETS \| status` | `FILTER_TICKETS \| closed` |
| Search Ticket | `SEARCH_TICKET \| ticket_id` | `SEARCH_TICKET \| 1001` |
| Update Ticket | `UPDATE_TICKET \| ticket_id \| status \| notes` | `UPDATE_TICKET \| 1001 \| closed \| Issue resolved` |
| View by Name | `VIEW_BY_NAME \| name` | `VIEW_BY_NAME \| John` |
| View by ID | `VIEW_BY_ID \| ticket_id` | `VIEW_BY_ID \| 1001` |
| Admin Logout | `ADMIN_LOGOUT` | `ADMIN_LOGOUT` |

## Testing

### Quick Test
```bash
# Terminal 1
python3 ServerSide.py

# Terminal 2
python3 ClientSide.py
# Then select options from the menu
```

### Automated Test (using TicketAPI)
```bash
# Terminal 1
python3 ServerSide.py

# Terminal 2
python3 TicketAPI.py
# This runs the test at the bottom of the file
```

## File Structure
```
Application/
├── ServerSide.py      ← Server (port 13000)
├── ClientSide.py      ← CLI reference client
├── TicketAPI.py       ← API layer for integration
└── WebServer.py       ← Optional: Flask web server (commented out)

html/
├── index.html         ← HTML interface (commented out)
├── js/
│   └── index.js       ← JavaScript (commented out)
└── styleSheets/
    └── index.css      ← CSS styles

Data/
├── LOGIN.csv          ← Admin credentials
└── DATA.csv           ← Ticket database
```

## Next Steps for HTML Frontend

To implement the HTML frontend:

1. **Create server.py** or use `WebServer.py` (currently commented out)
2. **Import TicketAPI** functions in your Flask/Python endpoints
3. **Map HTML form inputs** to TicketAPI function calls
4. **Display responses** from the API in the HTML interface

Example forms needed:
- Create Ticket Form (name, email, description)
- View Tickets Form (email input)
- Check Status Form (ticket_id, email)
- Filter Tickets Form (email, status dropdown)
- Admin Login Form (username, password)
- Admin Update Form (ticket_id, status, description)
- etc.

## Verification

All components follow the README.md protocol specification and handle:
✅ Customer operations (create, view, check status, filter)
✅ Admin operations (login, view all, search, update, filter, etc.)
✅ Error handling and validation
✅ Input sanitization
✅ Persistent socket connection
✅ Multi-threaded server for multiple clients
