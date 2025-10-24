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

hostname = socket.gethostname()


def main():
    runProgram()

def runProgram():
    verifyArgs()
    hostPort = getHostPort() 
    outputport = sys.argv[ARG_2]
    syslogport = sys.argv[ARG_3]

    currJob = -1
    completedJob = True 
    jobData = []

    outputsocket = mc.multicastSenderSocket()
    syslogsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(hostPort)
        serversocket.connect(hostPort)
        with serversocket:
            if completedJob: 
                message = "Fetching job...\n"
                syslogsocket.sendto(bytes(message, "utf-8"), (hostname, int(syslogport)))
                serversocket.sendall(b'GET')
                data = serversocket.recv(BUFFER_SIZE)
                dataText = data.decode('UTF-8').strip()
                print("RECEIVED:")
                print(dataText)
                if dataText != "No jobs are available":
                    completedJob=False
                    id_work = dataText.split(": ", 1)
                    currJob = id_work[0]
                    jobData = id_work[1].split(" ")
                    message = "Received job {}, starting work...\n".format(currJob)
                    syslogsocket.sendto(bytes(message, "utf-8"), (hostname, int(syslogport)))
                    work(jobData, outputsocket, outputport)
                else:
                    message = "No job available, trying again...\n"
                    syslogsocket.sendto(bytes(message, "utf-8"), (hostname, int(syslogport)))
            else:
                completedJob = True
                returnText = bytes("DONE {}".format(currJob), encoding="utf-8")
                serversocket.sendall(returnText)
                message = "Completed job {}\n".format(currJob)
                syslogsocket.sendto(bytes(message, "utf-8"), (hostname, int(syslogport)))

        time.sleep(1)

def work(workArray, outputsocket, outputport):
    for word in workArray:
        print(word)
        outputsocket.sendto(bytes(word, 'utf-8'), (MULTICAST_HOST, int(outputport)))
        time.sleep(0.25)


def verifyArgs():
    if len(sys.argv) != NUM_ARGS:
        raise ValueError("ERROR: Arguments must be in the form <serverport> <outputport> <syslogport>")
    elif sys.argv[ARG_1] == sys.argv[ARG_2] or sys.argv[ARG_1] == sys.argv[ARG_3] or sys.argv[ARG_2] == sys.argv[ARG_3]:
        raise ValueError("ERROR: Cannot use duplicate ports")

def getHostPort():
    hostPort = tuple(sys.argv[ARG_1].split(":", 1))

    if len(hostPort) < 2:
        if sys.argv[ARG_1].isdigit():
            hostPort = (socket.gethostname(), int(sys.argv[ARG_1]))
    
    return hostPort


if __name__=="__main__":
    main()