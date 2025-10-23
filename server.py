import select
import sys
import socket

hostname = socket.gethostname()
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
workersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

STATUS_WAITING = 'WAITING' 
STATUS_RUNNING = 'RUNNING' 
STATUS_COMPLETED = 'COMPLETED'

BUFFER_SIZE = 1024
ENCODING = 'utf-8'


class Queue:
    def __init__(self):
        self.dataQueue = []
        self.statusArray = []
        self.head = 0
    
    def getData(self, index):
        return self.dataQueue[index]
    
    def getStatus(self, index):
        return self.statusArray[index]
    
    def enqueue(self, jobValue):
        self.dataQueue.append(jobValue)
        self.statusArray.append(STATUS_WAITING)
        return len(self.dataQueue) - 1
    
    def dequeue(self):
        output = self.dataQueue[self.head]
        self.statusArray[self.head] = STATUS_WAITING
        self.head += 1
        return output

    def getDataQueue(self):
        return self.dataQueue

queue = Queue()


def main():
    runProgram()

def runProgram():
    try:
        verifyArgs()
        clientsocket.bind((hostname, int(sys.argv[1])))
        clientsocket.listen(5)

        workersocket.bind((hostname, int(sys.argv[2])))
        workersocket.listen(5)

        inputs = [ clientsocket, workersocket ]

        while inputs:
            readable, writable, exceptional = select.select(inputs, inputs, inputs)

            for socket in readable:
                conn,addr = socket.accept()
                returnText = ""
                with conn:
                    try:
                        if socket is clientsocket:
                            print('Connected by', addr)
                            data = conn.recv(BUFFER_SIZE)
                            dataText = data.decode('UTF-8').strip()
                            print("heard:")
                            print(dataText)
                            commandArray = dataText.split(" ", 1)
                            returnText = determineCommand(commandArray)
                            returnText = bytes(returnText, encoding=ENCODING)
                            print("Array is now: " + str(queue.getDataQueue()))
                        else:
                            print('Worker connected at address ', addr)
                            data = conn.recv(BUFFER_SIZE)
                            dataText = data.decode('UTF-8').strip()
                            print(dataText)
                            returnText = bytes(getJob(), encoding=ENCODING)
                        conn.sendall(returnText)
                        conn.close()
                    except Exception as e:
                        conn.sendall(bytes(str(e), ENCODING))   

    except Exception as e:
        print(e)

def verifyArgs():
    if len(sys.argv) != 3:
        raise ValueError("Arguments must be in the form <clientport> <workerport>")

def determineCommand(commandArray): 
    output = ""
    try:
        match commandArray[0]:
            case "JOB":
                output = addJob(commandArray[1])
            case "STATUS":
                output = statusJob(commandArray[1])
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

def determineWorkerRequest(request):
    if request == "GET":
        getJob(currElement)

def getJob():
    try: 
        output = queue.dequeue()
    except IndexError as e:
        raise ValueError("List is currently empty")
    return output 

def incrementQueue():
    currElement+=1

if __name__=="__main__":
    main()





