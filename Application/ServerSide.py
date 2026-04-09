#!/usr/sbin/python3
from socket import *
from _thread import *
from random import *

def TicketThread(connectSocket):
    print("* | Starting connection for service \n")
