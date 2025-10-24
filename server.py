"""
server.py
The server implementation for Assignment 1.

Author: Lyle Arcinas 
Course: COMP 3010
Term: Fall 2025
"""

import select
import sys
import socket

# Constants used to flag what status a job is in.
STATUS_WAITING = 'WAITING' 
STATUS_RUNNING = 'RUNNING' 
STATUS_COMPLETED = 'COMPLETED'

"""
class Queue

A class for my queue implementation. I use a class so I can instantiate an instance of Queue.
Note all elements stay in the queue. This is needed to get the status of completed jobs.
"""

INITIAL_INDEX = 0
OFFSET = 1

class Queue:
    def __init__(self):
        self.dataQueue = [] # Two arrays are used; one to hold the data for a job, the other to hold its status. Indices should point to the same job.
        self.statusArray = []
        self.head = INITIAL_INDEX
    
    def getData(self, index):
        return self.dataQueue[index]
    
    def getStatus(self, index):
        return self.statusArray[index]
    
    def finish(self, index):
        self.statusArray[index] = STATUS_COMPLETED
    
    def enqueue(self, jobValue):
        self.dataQueue.append(jobValue)
        self.statusArray.append(STATUS_WAITING)
        return len(self.dataQueue) - OFFSET 

    # Notice dequeue merely increments head and does not remove any data from the arrays. 
    def dequeue(self):
        output = "{}: {}".format(self.head,self.dataQueue[self.head])
        self.statusArray[self.head] = STATUS_WAITING
        self.head += OFFSET 
        return output # Returns a string with the data of the dequeued job

    def getDataQueue(self):
        return self.dataQueue
     
# Constants for sending strings as bytes
BUFFER_SIZE = 1024
ENCODING = 'utf-8'
BACKLOG = 5

# Constants for fetching instruction parameters
ARG_0 = 0
ARG_1 = 1
ARG_2 = 2
NUM_ARGS = 3


SPLIT_HALF = 1 # Used for splitting the client's commands in two

queue = Queue()
hostname = socket.gethostname()
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
workersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    runProgram()

def runProgram():
    try:
        verifyArgs() # Verifies that command parameters are in correct format
        clientsocket.bind((hostname, int(sys.argv[ARG_1])))
        clientsocket.listen(BACKLOG)

        workersocket.bind((hostname, int(sys.argv[ARG_2])))
        workersocket.listen(BACKLOG)

        inputs = [ clientsocket, workersocket ]

        while inputs: # Loops, making sure that all connected workers and clients are able to talk to the server
            readable, writable, exceptional = select.select(inputs, inputs, inputs)

            for socket in readable:
                conn,addr = socket.accept()
                returnText = ""
                with conn:
                    try:
                        # Both worker and client send commands in a format "COMMAND PARAMETER", so this splits it into its constituent parts
                        data = conn.recv(BUFFER_SIZE)
                        dataText = data.decode(ENCODING).strip()
                        commandArray = dataText.split(" ", SPLIT_HALF)

                        # If a client connects:
                        if socket is clientsocket:
                            # Print connection info into CMD
                            print("CLIENT CONNECTED AT ADDRESS {}".format(addr))
                            print("CLIENT > {}".format(dataText))

                            # Determines what to return to the client
                            returnText = determineCommand(commandArray)
                            returnText = bytes(returnText, encoding=ENCODING)
                        else:
                            # Also prints connection info into the cmd and determines work, but for a worker connection.
                            print("WORKER > {}".format(dataText))
                            returnText = determineWorkerRequest(commandArray)
                            print("WORKER < {}".format(returnText))
                            returnText = bytes(returnText, ENCODING)


                        conn.sendall(returnText)
                        conn.close()

                    except Exception as e: # If any exceptions
                        conn.sendall(bytes(str(e), ENCODING))   
    except Exception as e:
        print(e)
"""
verifyArgs()

Used to verify that the program was launched with the correct parameters.
"""
def verifyArgs():
    if len(sys.argv) != NUM_ARGS:
        raise ValueError("ERROR: Arguments must be in the form <clientport> <workerport>")
    elif sys.argv[ARG_1] == sys.argv[ARG_2]:
        raise ValueError("ERROR: Cannot use the same port for client and worker")

# Client methods
"""
determineCommand()

Used to determine what work we need to do given a client's inputs.
"""
def determineCommand(commandArray): 
    output = ""
    try:
        match commandArray[ARG_0]:
            case "JOB":
                output = addJob(commandArray[ARG_1])
            case "STATUS":
                output = statusJob(commandArray[ARG_1])
            case _: raise ValueError("ERROR: Commands should start with STATUS or JOB")
    except Exception as e:
        raise e

    return output 
"""
addJob()

Adds a new job into the queue and returns its ID.
"""
def addJob(jobValue):
    id = queue.enqueue(jobValue)
    returnText = "Received JOB with ID <{}>".format(str(id))

    return returnText 
"""
statusJob()

Returns the status for a given job ID.
"""
def statusJob(jobValue):
    if jobValue.isdigit():
        try:
            returnText = "Job {} is in status <{}>".format(jobValue, queue.getStatus(int(jobValue)))
        except IndexError as e:
            returnText = "Job {} does not exist".format(jobValue)
    else:
        raise ValueError("Second argument for STATUS command must be an int")

    return returnText

# Worker methods
"""
There are two headers a worker can send the server in my internal protocol:

GET: Getting the job at the front of the queue.
DONE <#>: Sets the job at ID # to completed.
"""

"""
determineWorkerRequest()

It takes in the input from the worker and determines which command it is sending the server; then, executes appropriately.
"""
def determineWorkerRequest(commandArray):
    output = ""
    try:
        match commandArray[ARG_0]:
            case "GET":
                output = getJob()
            case "DONE":
                output = finishJob(commandArray[ARG_1])
            case _:
                raise ValueError("Must either be GET or DONE")
    except Exception as e:
        raise e
    return output


"""
getJob()

Returns the job at the front of the queue.
"""
def getJob():
    output = "NO JOB"
    try: 
        output = queue.dequeue()
    except IndexError as e:
        raise ValueError(output)
    return output 
"""
finishJob()

Sets the job with the specified ID as completed.
"""
def finishJob(jobValue):
    output = ""
    if jobValue.isdigit():
        try:
            queue.finish(int(jobValue))
            output = "Completed job <{}>".format(jobValue)
        except IndexError as e:
            raise ValueError("Job <{}> does not exist".format(jobValue))
    else:
        raise ValueError("Second argument must be a job ID")
    
    return output

if __name__=="__main__":
    main()





