import select
import sys
import socket

queue = []
hostname = socket.gethostname()
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    runProgram()

def runProgram():
    try:
        verifyArgs()
        try:
            clientsocket.bind((hostname, int(sys.argv[1])))
            clientsocket.listen(5)

            while True:
                conn,addr = clientsocket.accept()
                with conn:
                    try:
                        print('Connected by', addr)
                        data = conn.recv(1024)
                        dataText = data.decode('UTF-8').strip()
                        print("heard:")
                        print(dataText)
                        queue.append(dataText) 
                        conn.sendall(b"Received ")
                        print("Array is now: " + str(queue))
                    except Exception as e:
                        print(e)
        except OSError as e:
            print(e)
    except ValueError as e:
        print(e)
    
    


def verifyArgs():
    if (sys.argv):
        if len(sys.argv) != 3:
            raise ValueError("Arguments must be in the form <clientport> <workerport>")


if __name__=="__main__":
    main()