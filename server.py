import select
import sys
import socket

STATUS_WAITING = 'WAITING' 
STATUS_RUNNING = 'RUNNING' 
STATUS_COMPLETED = 'COMPLETED'

class Queue:
    def __init__(self):
        self.dataQueue = []
        self.statusArray = []
        self.head = INITAL_INDEX
    
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
    
    def dequeue(self):
        output = "{}: {}".format(self.head,self.dataQueue[self.head])
        self.statusArray[self.head] = STATUS_WAITING
        self.head += OFFSET 
        return output

    def getDataQueue(self):
        return self.dataQueue

BUFFER_SIZE = 1024
ENCODING = 'utf-8'
BACKLOG = 5

ARG_0 = 0
ARG_1 = 1
ARG_2 = 2
NUM_ARGS = 3

INITAL_INDEX = 0
OFFSET = 1

SPLIT_HALF = 1

queue = Queue()
hostname = socket.gethostname()
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
workersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    runProgram()

def runProgram():
    try:
        verifyArgs()
        clientsocket.bind((hostname, int(sys.argv[ARG_1])))
        clientsocket.listen(BACKLOG)

        workersocket.bind((hostname, int(sys.argv[ARG_2])))
        workersocket.listen(BACKLOG)

        inputs = [ clientsocket, workersocket ]

        while inputs:
            readable, writable, exceptional = select.select(inputs, inputs, inputs)

            for socket in readable:
                conn,addr = socket.accept()
                returnText = ""
                with conn:
                    try:
                        data = conn.recv(BUFFER_SIZE)
                        dataText = data.decode(ENCODING).strip()
                        commandArray = dataText.split(" ", SPLIT_HALF)

                        if socket is clientsocket:
                            print("CLIENT CONNECTED AT ADDRESS {}".format(addr))
                            print("CLIENT > {}".format(dataText))
                            returnText = determineCommand(commandArray)
                            returnText = bytes(returnText, encoding=ENCODING)
                        else:
                            print("WORKER > {}".format(dataText))
                            returnText = determineWorkerRequest(commandArray)
                            print("WORKER < {}".format(returnText))
                            returnText = bytes(returnText, ENCODING)


                        conn.sendall(returnText)
                        conn.close()

                    except Exception as e:
                        conn.sendall(bytes(str(e), ENCODING))   
    except Exception as e:
        print(e)

def verifyArgs():
    if len(sys.argv) != NUM_ARGS:
        raise ValueError("ERROR: Arguments must be in the form <clientport> <workerport>")
    elif sys.argv[ARG_1] == sys.argv[ARG_2]:
        raise ValueError("ERROR: Cannot use the same port for client and worker")

# Client methods
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

def addJob(jobValue):
    id = queue.enqueue(jobValue)
    returnText = "Received JOB with ID <{}>".format(str(id))

    return returnText 

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

def getJob():
    output = "NO JOB"
    try: 
        output = queue.dequeue()
    except IndexError as e:
        raise ValueError(output)
    return output 

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





