"""
worker.py
The worker that pulls work from the server and sends it to a specified multicast port, as well as a specified syslog port.

Author: Lyle Arcinas 
Course: COMP 3010
Term: Fall 2025
"""
import sys
import socket
import time
import multicast as mc 

# Constants for sending strings as bytes
BUFFER_SIZE = 1024
ENCODING = "utf-8" 

# Constants for fetching instruction parameters
ARG_0 = 0
ARG_1 = 1
ARG_2 = 2
ARG_3 = 3
NUM_ARGS = 4

MULTICAST_HOST = "239.0.0.1" # Multicast host specified in assignment details

NO_JOB = "NO JOB" # Part of the internal protocol; how the server tells the worker there is no job in the queue.

SLEEP_CONSTANT = 0.25 # How long the worker will wait until doing more work; this is for printing data to the multicast, but the worker will also fetch jobs at a rate determined by this constant.

SPLIT_HALF = 1 # Used when we split a parameter "url:hostname" into an array.
HALF_SIZE = 2 # Used to check that the split happened; see getHostPort for more details

DEFAULT_JOB = -1 # Impossible value for setting the inital value of currJob, which tracks which job the worker is on.

hostname = socket.gethostname()

def main():
    runProgram()

"""
runProgram()

The default looping part of the worker. Continually sends GET commands to the server, and works on available jobs.
"""
def runProgram():
    verifyArgs() # Throws an error if cmd parameters are not in the correct format
    hostPort = getHostPort() 
    outputPort = int(sys.argv[ARG_2])
    syslogPort = int(sys.argv[ARG_3])

    currJob = DEFAULT_JOB 
    completedJob = True 
    jobData = []

    outputSocket = mc.multicastSenderSocket()
    syslogSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Since this is a UDP socket, we only need to create it once

    while True:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creates new sockets for each loop
        serversocket.connect(hostPort)

        with serversocket:
            # completedJob is true either if we just finished a job or if we have not worked on a job yet.
            if completedJob: 
                # Sends message to syslog server that we are working on getting a new job 
                message = "Fetching job...\n"
                syslogSocket.sendto(bytes(message, ENCODING), (hostname, syslogPort))

                # Sends a GET request to the server to get the next job in the queue
                serversocket.sendall(b'GET')
                print('SERVER < GET')

                # Receives the response from server and prints it to cmd
                data = serversocket.recv(BUFFER_SIZE)
                dataText = data.decode(ENCODING).strip()
                print("SERVER > {}".format(dataText))

                # If the server DOES return with a job: 
                if dataText != NO_JOB:
                    completedJob = False # Set this to false to let next loop know we need to push a DONE

                    # Processes what the server returns, splits it into two for further work
                    commandArray = dataText.split(": ", 1)
                    currJob = commandArray[0]
                    jobData = commandArray[1].split(" ")

                    # Work starts on the current job, with a notice posted to the cmd and syslog
                    message = "Received job {}, starting work...\n".format(currJob)
                    syslogSocket.sendto(bytes(message, ENCODING), (hostname, syslogPort))
                    work(jobData, outputSocket, outputPort)
                else:
                    # Just loops if there is no job
                    message = "No job available, trying again...\n"
                    syslogSocket.sendto(bytes(message, ENCODING), (hostname, syslogPort))
            else:
                # If completedJob is false, we know we need to let the server know we're done
                completedJob = True

                # Sends the DONE command to the server
                returnText = bytes("DONE {}".format(currJob), encoding=ENCODING)
                serversocket.sendall(returnText)

                # Prints completion to cmd and syslog
                print('SERVER < DONE {}'.format(currJob))
                message = "Completed job {}\n".format(currJob)
                syslogSocket.sendto(bytes(message, ENCODING), (hostname, syslogPort))

        time.sleep(SLEEP_CONSTANT) # Will send requests at rate of SLEEP_CONSTANT

"""
verifyArgs()

Used to verify that the program was launched with the correct parameters.
"""
def verifyArgs():
    if len(sys.argv) != NUM_ARGS:
        raise ValueError("ERROR: Arguments must be in the form <serverPort> <outputPort> <syslogPort>")
    elif sys.argv[ARG_1] == sys.argv[ARG_2] or sys.argv[ARG_1] == sys.argv[ARG_3] or sys.argv[ARG_2] == sys.argv[ARG_3]:
        raise ValueError("ERROR: Cannot use duplicate ports")
    elif not sys.argv[ARG_2].isdigit() or not sys.argv[ARG_3].isdigit():
        raise ValueError("ERROR: Ports must be digits")

"""
work()

Actually completes the work of casting one word of a time to a multicast server.
It uses outputSocket and outputPort from runProgram() to send the messages.
"""
def work(workArray, outputSocket, outputPort):
    for word in workArray:
        print("SENDING: {} ".format(word))
        outputSocket.sendto(bytes("Data: {}".format(word), ENCODING), (MULTICAST_HOST, outputPort))
        time.sleep(SLEEP_CONSTANT)


"""
getHostPort()

If the user provides the server url, i.e., falcon.cs.umanitoba.ca:55000, it will use the full URL and port. Otherwise it defaults to the localhost.
"""
def getHostPort():
    hostPort = tuple(sys.argv[ARG_1].split(":", SPLIT_HALF))

    if len(hostPort) < HALF_SIZE:
        if sys.argv[ARG_1].isdigit():
            hostPort = (socket.gethostname(), int(sys.argv[ARG_1]))
    
    return hostPort


if __name__=="__main__":
    main()