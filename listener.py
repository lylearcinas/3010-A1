import multicast
import socket

port = 55002
hostname = "239.0.0.1"


def main():
    print(hostname)
    listensocket = multicast.multicastReceiverSocket(hostname, port)
    while True:
        data = listensocket.recv(1024)
        print(data)

if __name__=="__main__":
    main()