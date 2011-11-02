from socket import *

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
        #print e
        print "cannot connect to " + HOST + ' on ' + str(PORT)
        continue
    while 1:
        data = raw_input('Enter a command')

        tcpCliSock.send(data)
        
        if data == 'exit':
            break
        
        has_data = True
        #while has_data:
         #   print '1'
        new_dat = tcpCliSock.recv(BUFSIZ)
        #    if new_dat == None or new_dat == '' or new_dat == 0:
         #       break
        print new_dat , 'is new data'
        #print 'out'
    tcpCliSock.close()
