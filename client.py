from socket import *
import os

#need to make it so ls can accept arguments (done server-side)

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
    new_dat = ''
    while 1:
        
        #this code gets a file size (in bytes)
        #f = os.stat(r'C:\Users\Hayden\Dr.-Who-s-Piggybank\README')
        #print f.st_size
        
        if new_dat == 'pwd':
            user_name = raw_input("Please enter a user name: ")
            pw = raw_input("Please enter a password: ")
            
            #will need to send here, but server needs to be ready
        
        else:    
            data = raw_input('Enter a command')
            
            #preparing for put
            if data[0:3] == 'put':
                file_path = data.replace(' ', '')[3:]
                sender = open(file_path)
                print sender
            
            elif data[0:4] == 'mput':
                files = data[4:]
                if files == '*':
                    #will need to query current directory (I guess) and send all files
                    print 'placeholder'
                else:
                    files = files.split()
                    #now send all files
                    for i in range(0, len(files)):
                        sender = open(files[i])
                        #send sender
            
            #needs to become quit
            elif data == 'exit':
                tcpCliSock.send(data)
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
