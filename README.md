[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ProjectCS460/Project-Repo)
# Project Repository
For COMPSCI 460 at University of Wisconsin Whitewater

## Key Commands Summary

| Action        | Command                                   |
|---------------|--------------------------------------------|
| Clone         | `git clone https://github.com/ProjectCS460/Project-Repo`    |
| Check Status  | `git status`                               |
| Stage         | `git add <file>` or `git add .`            |
| Commit        | `git commit -m "message"`                  |
| Push          | `git push origin <branch-name>`            |

Requirements for development: $Python \le 3.10$, Code editor, (optional) VM enviroment.



## Project Idea:
As a group we will develop a client-server based ticket application. For this project we will specify it for a system of helpdesk type tickets. This implies that a user can submit their information/email and store a process of what the user is having problems with. This will allow another person or “admin” to log into the client and see greater access to the database. The server will manage the ticket database and remain up so that at any point the client will be able to reach out and put in “requests”. While the client will remain a user interface where you can choose to submit a ticket or log in to see them. All of the login will handle privilege and what you can see on the system. This project will demonstrate Client server communication. The admin will not be able to reach out to users directly but may update the status of the tickets. The tickets will maintain a number, a user(name), a short description, a status, a timestamp, and a long description field for admin updates.

## Requirements:

### Client

#### Basic User (Non‑Admin / Customer)
+ Connect to the ticket server.
+ Create tickets.
+ View own tickets only.
+ Allow customers to check the status of their own ticket using ticket number/email.
+ Filter own tickets from open to closed.
+ Disconnect after ticket submission.
+ Handle invalid input.
+ User‑based GUI for non‑admin.
+ Display server responses in a clean readable format.
+ Return to main menu after each action.
+ Prevent access to admin‑only functions.
+ Validate customer identity when checking ticket status.
+ Handle malformed or incomplete protocol messages.

#### Admin User
+ Connect to the ticket server.
+ View list of all tickets.
+ Filter all tickets from open to closed.
+ Admin update ticket status and long description.
+ Allow admin to search for ticket number.
+ Log out and disconnect.
+ Handle invalid input.
+ Create tickets (admins can also submit tickets).
+ View full ticket details (name, email, description, timestamp).
+ View tickets filtered by customer name.
+ View tickets filtered by ticket ID.
+ Access admin‑specific GUI/menu.
+ Maintain session until logout.
+ Receive confirmation messages after updates.
+ Display server‑formatted ticket database output.
+ Prevent unauthorized access (must authenticate first).

### Server
+ Contain ticket database.
+ Maintain ticket number system
+ Print out a clean format to the admin user.
+ Validate admin user.
+ Send structured responses separately based on privilege in system.
+ Verify customer identity when checking status.
+ Store updated ticket information after admin changes.

Protocol Design (Unified Format)
All messages in the system follow a standardized structure using the format COMMAND | field1 | field2 | … followed by a newline character. This ensures consistent communication between client and server. Server responses follow the format SUCCESS | message | optional_data or ERROR | message, depending on the outcome of the request.

Client → Server Requests
Basic User (Customer)
Customers interact with the system using the following protocol messages:

CREATE_TICKET | name | email | short_description  
Used when a customer submits a new helpdesk ticket.

CHECK_STATUS | ticket_id | email  
Allows a customer to check the status of their own ticket.

VIEW_MY_TICKETS | email  
Retrieves all tickets associated with the customer’s email.

FILTER_MY_TICKETS | email | status  
Filters the customer’s tickets by status (e.g., open or closed).

DISCONNECT  
Ends the client session after completing actions.

Admin User
Admins have elevated privileges and use the following protocol messages:

ADMIN_LOGIN | username | password  
Authenticates an admin user before granting access.

VIEW_ALL_TICKETS  
Retrieves the full ticket database.

FILTER_TICKETS | status  
Filters all tickets by status.

SEARCH_TICKET | ticket_id  
Searches for a specific ticket by its ID.

UPDATE_TICKET | ticket_id | new_status | long_description  
Allows admins to update ticket status and add detailed notes.

CREATE_TICKET | name | email | short_description  
Admins may also create tickets on behalf of users.

VIEW_BY_NAME | customer_name  
Retrieves tickets associated with a specific customer name.

VIEW_BY_ID | ticket_id  
Retrieves full details of a specific ticket.

ADMIN_LOGOUT  
Ends the admin session.

Server → Client Responses
The server responds to client requests using structured messages:

SUCCESS | TICKET_CREATED | ticket_id  
Confirms successful ticket creation.

SUCCESS | STATUS | ticket_id | status | timestamp | long_description  
Returns the full status of a ticket.

SUCCESS | TICKET_LIST | ticket1_data ; ticket2_data ; …  
Sends a list of tickets to the client.

SUCCESS | FILTERED_LIST | ticket1_data ; ticket2_data ; …  
Sends a filtered list of tickets.

SUCCESS | ADMIN_AUTHENTICATED  
Confirms successful admin login.

SUCCESS | TICKET_UPDATED | ticket_id | new_status | long_description  
Confirms that a ticket was successfully updated.

SUCCESS | TICKET_FOUND | ticket_data  
Returns the details of a searched ticket.

ERROR | message  
Indicates that an error occurred, such as invalid input or unauthorized access.

Client‑Side Processing
The client processes incoming server responses as follows:

 &nbsp; When creating a ticket, the client sends a CREATE_TICKET message and waits for a SUCCESS response containing the new ticket ID, which is then displayed to the user.

&nbsp; When checking ticket status, the client sends CHECK_STATUS and waits for a STATUS response containing the ticket’s details.

&nbsp; When viewing or filtering tickets, the client receives a TICKET_LIST or FILTERED_LIST response and displays the results in a readable format.

&nbsp; When logging in as an admin, the client sends ADMIN_LOGIN and waits for ADMIN_AUTHENTICATED before showing admin‑only options.

&nbsp; When updating a ticket, the client receives TICKET_UPDATED and displays the updated information.

&nbsp; When receiving an ERROR response, the client displays the error message and returns the user to the main menu.

Server‑Side Processing
 &nbsp; The server handles requests and manages the ticket database using the following logic:

 &nbsp; On startup, the server loads the ticket database, initializes the ticket numbering system, and prepares admin authentication data.

 &nbsp; When receiving CREATE_TICKET, the server parses the fields, assigns a new ticket ID, stores the ticket, and responds with TICKET_CREATED.

 &nbsp; When receiving CHECK_STATUS, the server verifies that the email matches the ticket owner before returning ticket details or an error.

 &nbsp; When receiving VIEW_MY_TICKETS, the server filters tickets by email and returns the list.

 &nbsp; When receiving VIEW_ALL_TICKETS, the server returns the full ticket database to the admin.
  
 &nbsp; When receiving FILTER_TICKETS, the server filters tickets by status and returns the results.

 &nbsp; When receiving SEARCH_TICKET, the server locates the ticket by ID and returns it or sends an error.

 &nbsp; When receiving UPDATE_TICKET, the server validates admin privileges, updates the ticket’s status and long description, saves the changes, and returns TICKET_UPDATED.

 &nbsp; When receiving ADMIN_LOGIN, the server validates credentials and returns either ADMIN_AUTHENTICATED or an error.

 &nbsp; For any malformed or invalid request, the server responds with an ERROR message.


## Work Division:
+ Member A will work on the client side communication for admin (find, edit, status func's) and ticket submission for users.
+ Member B will work on the client side communication for user includes user GUI and login GUI. 
+ JacobT2006 will work on the server side communication between the client UI and the database with login validation.
