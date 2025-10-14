import select
import sys
import socket


def main():
    getArgs()

def getArgs():
    if len(sys.argv) != 3:
        raise ValueError("Arguments must be in the form <clientport> <workerport>")

if __name__=="__main__":
    main()