import select
import sys
import socket

hostname = socket.gethostname()
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    runProgram()

def runProgram():
    try:
        verifyArgs()
    except ValueError as e:
        print(e)

    try:
        clientsocket.bind((hostname, int(sys.argv[1])))
    except OSError as e:
        print(e)
    
    clientsocket.listen(5)

    while True:
        conn,addr = clientsocket.accept()
        with conn:
            try:
                print('Connected by', addr)
                data = conn.recv(1024)
                print("heard:")
                print(data.decode('UTF-8'))
                conn.sendall(b"hello")
            except Exception as e:
                print(e)


def verifyArgs():
    if len(sys.argv) != 3:
        raise ValueError("Arguments must be in the form <clientport> <workerport>")


if __name__=="__main__":
    main()