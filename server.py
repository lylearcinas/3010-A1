import select
import sys
import socket

hostname = socket.gethostname()
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    bindSockets()

def bindSockets():
    try:
        verifyArgs()
    except ValueError as e:
        print(e)

    try:
        clientsocket.bind((hostname, sys.argv[1]))
    except OSError as e:
        print(e)


def verifyArgs():
    if len(sys.argv) != 3:
        raise ValueError("Arguments must be in the form <clientport> <workerport>")


if __name__=="__main__":
    main()