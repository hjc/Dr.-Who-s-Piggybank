from socket import *
#purposes
tcpCliSock = socket(AF_INET, SOCK_STREAM)
while 1:
    HOST = raw_input("Please enter a host name or exit to terminate the client.\n")
    HOST = gethostbyname(HOST)

    if HOST == 'exit':
        break

    PORT = int(raw_input("Please enter a port to connect to.\n"))
#HOST = 'localhost'
#PORT = 21566
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    try:
        tcpCliSock.connect(ADDR)
        print 'connected to: ' + HOST + ' on ' + str(PORT)

    except error as e:
        print e
        print "cannot connect to " + HOST + ' on ' + str(PORT)
        continue
    while 1:
        data = raw_input()

        tcpCliSock.send(data)
        
        if data == 'exit':
            break
        
        new_dat = tcpCliSock.recv(BUFSIZ)
        print new_dat
    tcpCliSock.close()
