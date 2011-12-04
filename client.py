def get_file_name(path):
    name = ''
    for i in range(len(path) - 1, -1, -1):
        if (path[i] == '/' or path[i] == '\\'):
            break
        name += path[i]
    return name[::-1]


from socket import *
import os, getpass, math

#need to make it so ls can accept arguments (done server-side)
#tcpCliSock = socket(AF_INET, SOCK_STREAM)

while 1:
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    HOST = raw_input("Please enter a host name or exit to terminate the client.\n")
    HOST = gethostbyname(HOST)

    if HOST == 'exit':
        break

    PORT = int(raw_input("Please enter a port to connect to.\n"))
    #HOST = 'localhost'
    #PORT = 21566
    BUFSIZ = 2048
    ADDR = (HOST, PORT)
    new_dat = ''

    try:
        tcpCliSock.connect(ADDR)
        print 'Connected to: ' + HOST + ' on ' + str(PORT)
        new_dat = tcpCliSock.recv(BUFSIZ)

    except error as e:
        #print e
        print "Cannot connect to " + HOST + ' on ' + str(PORT)
        continue
    
    while 1:
        
        #this code gets a file size (in bytes)
        #f = os.stat(r'C:\Users\Hayden\Dr.-Who-s-Piggybank\README')
        #print f.st_size
        
        if new_dat == 'pwd':
            user_name = raw_input("Please enter a user name: ")
            pw = getpass.getpass()
            
            user_string = 'USER:' + user_name + '!@!PASSWORD:' + pw 
            
            tcpCliSock.send(user_string)
            
            new_dat = tcpCliSock.recv(BUFSIZ)
            
            if new_dat == 'entry':
                print 'Welcome to the server!'
                continue
            else:
                print new_dat
                tcpCliSock.close()
                break
            #will need to send here, but server needs to be ready
        
        else:    
            data = raw_input('Enter a command')
            
            if data[0:2] == 'ls':
                tcpCliSock.send(data)
                new_dat = tcpCliSock.recv(BUFSIZ)
                print new_dat
                
            elif data[0:2] == 'cd':
                tcpCliSock.send(data)
                
            #preparing for put
            elif data[0:3] == 'put':
                file_path = data.replace(' ', '')[3:]
                if (file_path[0] != "\\" and file_path[0] != "/"):
                    if (os.name == 'nt'):
                        file_path = os.getcwd() + '\\' + file_path
                    else:
                        file_path = os.getcwd() + '/' + file_path
                sender = open(file_path).read()
                f = os.stat(file_path)
                f_size = f.st_size * 8.0
                #print f_size
                packets = math.ceil(f_size / BUFSIZ)
                file_descriptor = 'put FN:' + get_file_name(file_path)
                file_descriptor += '!@!'
                file_descriptor += 'PACKETS:'
                file_descriptor += str(int(packets))
                tcpCliSock.send(file_descriptor)
                
                for i in range(0, int(packets)):
                    tcpCliSock.send(sender[i*BUFSIZ:(i + 1) * BUFSIZ])
                #print file_descriptor
                
                #print sender
            
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
        #new_dat = tcpCliSock.recv(BUFSIZ)
        

            
        #    if new_dat == None or new_dat == '' or new_dat == 0:
         #       break
        #print new_dat , 'is new data'
        #print 'out'
    tcpCliSock.close()