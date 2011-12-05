def get_file_name(path):
    name = ''
    for i in range(len(path) - 1, -1, -1):
        if (path[i] == '/' or path[i] == '\\'):
            break
        name += path[i]
    return name[::-1]


from socket import *
import os, getpass, math, re
from stat import *

#need to make it so ls can accept arguments (done server-side)
#tcpCliSock = socket(AF_INET, SOCK_STREAM)

splitter = re.compile('\!@\!')

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
                if (file_path[0] != "\\" and file_path[0] != "/" and file_path[0] != 'C'):
                    if (os.name == 'nt'):
                        file_path = os.getcwd() + '\\' + file_path
                    else:
                        file_path = os.getcwd() + '/' + file_path
                        
                try:
                    sender = open(file_path).read()
                    
                except:
                    print 'File located at: ' + file_path + ' not found.'
                    continue

                file_descriptor = 'put FN:' + get_file_name(file_path)
                tcpCliSock.send(file_descriptor)
                
                tcpCliSock.send(sender)
                tcpCliSock.send('>>>~~FILE~~DONE~~<<<')
                
            
            elif data[0:3] == 'get':
                file_wanted = data[4:]
                fd = 'get FN:' + file_wanted
                tcpCliSock.send(fd)
                
                new_dat = tcpCliSock.recv(BUFSIZ)
                if (new_dat[0:5] == 'Error'):
                    print new_dat
                else:
                    f_info = splitter.split(new_dat)
                    fn = f_info[0][7:]
                    fn = get_file_name(fn)
                    print fn
                    #packets = f_info[1][8:]
                    #print packets
                    
                    file_data = ''
                    done = False
                    
                    while (not done):
                        dat = tcpCliSock.recv(BUFSIZ)
                        if '>>>~~FILE~~DONE~~<<<' in dat:
                            dat = dat.replace('>>>~~FILE~~DONE~~<<<', '')
                            done = True
                        file_data += dat
                    #for i in range(0, int(packets)):
                    #    file_data += tcpCliSock.recv(BUFSIZ)
                    
                    if '.' not in fn:
                        fn += '.txt'
                    
                    
                    writer = open(fn, 'w')
                    writer.write(file_data)
                    writer.close()
                    
                    print fn + ' received successfully'
                    #print file_data
            
            elif data[0:4] == 'mput':
                files = data[5:]
                if files[-1] == '*':
                    file_path = files[:-1]
                    if not file_path.strip():
                        file_path = os.getcwd()
                    contents = os.listdir(file_path)
                    #print contents
                    files = []
                    for i in range(0, len(contents)):
                        if (os.name == 'nt'):
                            this_path = file_path + '\\' + contents[i]
                        #    mode = os.stat(file_path + '\\' + contents[i]).st_mode
                        else:
                            this_path = file_path + '/' + contents[i]
                        mode = os.stat(this_path).st_mode
                        if not S_ISDIR(mode):
                            files.append(this_path)
                    #will need to query current directory (I guess) and send all files
                    print files
                    
                else:
                    files = files.split()
                
                fd = 'mput FILES:' + str(len(files))
                tcpCliSock.send(fd)
                #print files
                
                #now send all files
                for i in range(0, len(files)):
                    tcpCliSock.recv(BUFSIZ)
                    sender = open(files[i])
                    file_path = files[i]
                    if (file_path[0] != "\\" and file_path[0] != "/" and file_path[0] != 'C'):
                        if (os.name == 'nt'):
                            file_path = os.getcwd() + '\\' + file_path
                        else:
                            file_path = os.getcwd() + '/' + file_path
                            
                    try:        
                        sender = open(file_path).read()
                        
                    except:
                        print 'File located at: ' + file_path + ' not found. Ignoring \
                        and moving on.'
    
                    file_descriptor = 'put FN:' + get_file_name(file_path)
                    print file_descriptor
                    tcpCliSock.send(file_descriptor)
                    
                    tcpCliSock.send(sender)
                    tcpCliSock.send('>>>~~FILE~~DONE~~<<<')
                    #send sender
                    
            elif data[0:4] == 'mget':
                files = data[0:5]
                tcpCliSock.send(data)
                
                data = tcpCliSock.recv(BUFSIZ)
                fnum = data[11:]
                
                for i in range(0, int(fnum)):
                    tcpCliSock.send('begin transfer number: ' + str(i))
                    
                    data = tcpCliSock.recv(BUFSIZ)
                    
                    pieces = splitter.split(data)
                    fn = pieces[0][7:]
                    
                    if '.' not in fn:
                        fn += '.txt'
                        
                    f = ''
                    done = False
                    
                    while(not done):
                        dat = tcpCliSock.recv(BUFSIZ)
                        
                        if ('>>>~~FILE~~DONE~~<<<' in dat):
                            done = True
                            dat = dat.replace('>>>~~FILE~~DONE~~<<<', '')
                            
                        f += dat
                    stor = open(fn, 'w')
                    stor.write(f)
                    stor.close()
                    print fn, 'successfully received.'
                
            
            #needs to become quit
            elif data == 'exit':
                tcpCliSock.send(data)
                break
        
        has_data = True
        #while has_data:
         #   print '1'
        #new_dat = tcpCliSock.recv(BUFSIZ)
        #

            
        #    if new_dat == None or new_dat == '' or new_dat == 0:
         #       break
        #print new_dat , 'is new data'
        #print 'out'
    tcpCliSock.close()