# Echo server program
import socket
import os
from string import rstrip

#HOST = socket.gethostbyname(socket.gethostname())
HOST = 'localhost'
PORT = 50007
print 'Server hosted on ' + str(HOST) + ' Port ' + str(PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(2)

while 1:
    print 'Waiting for Connection....'
    conn, addr = s.accept()
    print 'Connected by', addr
    #workingdir = os.curdir
    os.chdir(r'C:/')
    
    while 1:
        data = conn.recv(1024)
        print data

        if data == 'exit':
            break
        elif not data:
            break
        elif data == 'ls':
            dirs = os.listdir(os.getcwd())
            the_dirs = "\n".join(dirs)
            conn.sendall(the_dirs)
            print 'did ls'

        elif data == 'os':
            conn.send('os is ' + os.name)
            
        elif data[0:2] == 'cd':
            try:
                os.chdir(rstrip(data[3:]))
                conn.send('Changed working directory to: ' + os.getcwd())
            except error as e: 
                conn.send('Directory: ' + data[3:] + ' not found in: ' + os.getcwd())
        
        elif data == 'thisdir':
            conn.send(os.getcwd())
            print 'did thisdir'
            
        else:
            conn.send(data)
    conn.close()
    print 'Disconnected by', addr
