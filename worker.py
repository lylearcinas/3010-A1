import sys
import socket
import time

ARG_0 = 0
ARG_1 = 1
ARG_2 = 2
ARG_3 = 3
NUM_ARGS = 4

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()

def main():
    runProgram()

def runProgram():
    try:
        verifyArgs()
        serversocket.bind((hostname, int(sys.argv[ARG_1])))
        serversocket.listen(5)

        while True:
            conn, addr = serversocket.accept()

            print('Connected by', addr)
            print("heard:")
            print(dataText)

            conn.close()
    except Exception as e:
        print(e)

def verifyArgs():
    if len(sys.argv) != NUM_ARGS:
        raise ValueError("ERROR: Arguments must be in the form <serverport> <outputport> <syslogport>")
    elif sys.argv[ARG_1] == sys.argv[ARG_2] or sys.argv[ARG_1] == sys.argv[ARG_3] or sys.argv[ARG_2] == sys.argv[ARG_3]:
        raise ValueError("ERROR: Cannot use duplicate ports")


if __name__=="__main__":
    main()