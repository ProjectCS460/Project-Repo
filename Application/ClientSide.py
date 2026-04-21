# Ticket App Client V1
# VERSION 1: 	Handles connection to ServerSide and client-side UI
# AUTHOR: 		jzabawski3453 & MysticalSkeptic
# CREATED: 		04/9/2026

#!/usr/bin/python3
from socket import *
import sys

#------------------------------------------------------------
# Server connection

serverSocket = None

def connect_to_server(host="127.0.0.1", port=13000):
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
        response = serverSocket.recv(1024).decode()
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
# Main client initialization

def main():
    """Initialize client and connect to server"""
    print("* Ticket App Client V1\n")
    
    # Connect to server
    if not connect_to_server():
        print("* | Exiting client\n")
        sys.exit(1)
    
    print("* | Client ready to communicate with server\n")
    
    # Keep connection active
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n* | Shutting down client\n")
        disconnect_from_server()

#------------------------------------------------------------

if __name__ == "__main__":
    main()

