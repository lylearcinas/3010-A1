"""
listener.py

A not-actually-needed script used only to test the multicast function. Submitting for posterity.

Author: Lyle Arcinas 
Course: COMP 3010
Term: Fall 2025
"""
import multicast
import socket

port = 55002
hostname = "239.0.0.1" # as specified in the assignment

def main():
    listensocket = multicast.multicastReceiverSocket(hostname, port)
    while True:
        data = listensocket.recv(1024)
        dataText = data.decode('UTF-8')
        print(dataText)

if __name__=="__main__":
    main()