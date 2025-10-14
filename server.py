import select
import sys
import socket


def main():
    print(sys.argv)
    if sys.argv[1] == "arg1":
        print("Yippee")
    else:
        print("Nooo")

if __name__=="__main__":
    main()