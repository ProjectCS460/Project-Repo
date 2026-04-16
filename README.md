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

## Protocol Design:
For our design of this project we will use the format: FOR_EXAMPLE | “Message here”. This will be used in conjunction with \n to clearly label responses and messages to and from for any part of the project. As well as listed examples below

Customer Create Ticket:  
+ CREATE_TICKET | name | email | short_description \n

Customer Check Status:  
+ CHECK_STATUS | ticket_id | email \n

Admin Login:  
+ ADMIN_LOGIN | username | password \n

Admin Update Ticket:  
+ UPDATE_STATUS | ticket_id | new_status | long_description \n

Server Response Format:  
+ SUCCESS | message | optional_data \n  
+ ERROR | message \n


## Work Division:
+ Member A will work on the client side communication for admin (find, edit, status func's) and ticket submission for users.
+ Member B will work on the client side communication for user includes user GUI and login GUI. 
+ JacobT2006 will work on the server side communication between the client UI and the database with login validation.
