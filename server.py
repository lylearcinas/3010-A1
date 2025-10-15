import select
import sys
import socket

dataQueue = []
statusArray = []
hostname = socket.gethostname()
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

STATUS_WAITING = 'WAITING' 
STATUS_RUNNING = 'RUNNING' 
STATUS_COMPLETED = 'COMPLETED'

def main():
    runProgram()

def runProgram():
    try:
        verifyArgs()
        clientsocket.bind((hostname, int(sys.argv[1])))
        clientsocket.listen(5)

        while True:
            conn,addr = clientsocket.accept()

            with conn:
                print('Connected by', addr)
                data = conn.recv(1024)
                dataText = data.decode('UTF-8').strip()
                print("heard:")
                print(dataText)
                commandArray = dataText.split(" ", 1)
                try:
                    returnText = determineCommand(commandArray)
                    returnText = bytes(returnText, encoding='utf8')
                    conn.sendall(returnText)
                    print("Array is now: " + str(dataQueue))
                except ValueError as e:
                    conn.sendall(bytes(str(e), 'utf-8'))
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
            case _: raise ValueError("Commands should start with STATUS or JOB")
    except ValueError as e:
        raise e

    return output 

def addJob(jobValue):
    dataQueue.append(jobValue)
    statusArray.append(STATUS_WAITING)
    returnText = "Received JOB with ID <{}>".format(str(len(dataQueue)-1))

    return returnText 

def statusJob(jobValue):
    if jobValue.isdigit():
        try:
            returnText = "Job {} is in status <{}>".format(jobValue, statusArray[int(jobValue)])
        except IndexError as e:
            returnText = "Job {} does not exist".format(jobValue)
    else:
        raise ValueError("Second argument for STATUS command must be an int")

    return returnText

if __name__=="__main__":
    main()