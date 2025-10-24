import sys
import socket
import time
import multicast as mc 

BUFFER_SIZE = 1024

ARG_0 = 0
ARG_1 = 1
ARG_2 = 2
ARG_3 = 3
NUM_ARGS = 4

MULTICAST_HOST = "239.0.0.1"
NO_JOB = "NO JOB"

SLEEP_CONSTANT = 0.25

SPLIT_HALF = 1
HALF_SIZE = 2

hostname = socket.gethostname()

def main():
    runProgram()

def runProgram():
    verifyArgs()
    hostPort = getHostPort() 
    outputPort = int(sys.argv[ARG_2])
    syslogPort = int(sys.argv[ARG_3])

    currJob = -1
    completedJob = True 
    jobData = []

    outputSocket = mc.multicastSenderSocket()
    syslogSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.connect(hostPort)
        with serversocket:
            if completedJob: 
                message = "Fetching job...\n"
                syslogSocket.sendto(bytes(message, "utf-8"), (hostname, syslogPort))
                serversocket.sendall(b'GET')
                print('SERVER < GET')
                data = serversocket.recv(BUFFER_SIZE)
                dataText = data.decode('UTF-8').strip()
                print("SERVER > {}".format(dataText))
                if dataText != NO_JOB:
                    completedJob=False
                    commandArray = dataText.split(": ", 1)
                    currJob = commandArray[0]
                    jobData = commandArray[1].split(" ")
                    message = "Received job {}, starting work...\n".format(currJob)
                    syslogSocket.sendto(bytes(message, "utf-8"), (hostname, syslogPort))
                    work(jobData, outputSocket, outputPort)
                else:
                    message = "No job available, trying again...\n"
                    syslogSocket.sendto(bytes(message, "utf-8"), (hostname, syslogPort))
            else:
                completedJob = True
                returnText = bytes("DONE {}".format(currJob), encoding="utf-8")
                print('SERVER < DONE {}'.format(currJob))
                serversocket.sendall(returnText)
                message = "Completed job {}\n".format(currJob)
                syslogSocket.sendto(bytes(message, "utf-8"), (hostname, syslogPort))

        time.sleep(SLEEP_CONSTANT)

def work(workArray, outputSocket, outputPort):
    for word in workArray:
        print("SENDING: {} ".format(word))
        outputSocket.sendto(bytes("Data: {}".format(word), 'utf-8'), (MULTICAST_HOST, outputPort))
        time.sleep(SLEEP_CONSTANT)


def verifyArgs():
    if len(sys.argv) != NUM_ARGS:
        raise ValueError("ERROR: Arguments must be in the form <serverPort> <outputPort> <syslogPort>")
    elif sys.argv[ARG_1] == sys.argv[ARG_2] or sys.argv[ARG_1] == sys.argv[ARG_3] or sys.argv[ARG_2] == sys.argv[ARG_3]:
        raise ValueError("ERROR: Cannot use duplicate ports")
    elif not sys.argv[ARG_2].isdigit() or not sys.argv[ARG_3].isdigit():
        raise ValueError("ERROR: Ports must be digits")

def getHostPort():
    hostPort = tuple(sys.argv[ARG_1].split(":", SPLIT_HALF))

    if len(hostPort) < HALF_SIZE:
        if sys.argv[ARG_1].isdigit():
            hostPort = (socket.gethostname(), int(sys.argv[ARG_1]))
    
    return hostPort


if __name__=="__main__":
    main()