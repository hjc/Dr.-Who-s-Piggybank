# Echo server program
#a
import socket
import os

HOST = socket.gethostbyname(socket.gethostname())
PORT = 50007
print 'Server hosted on ' + str(HOST) + ' Port ' + str(PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

while 1:
    print 'Waiting for Connection....'
    conn, addr = s.accept()
    print 'Connected by', addr
    workingdir = os.curdir
    
    while 1:
        data = conn.recv(1024)

        if data == 'exit':
            break
        elif not data:
            break
        elif data == 'ls':
            dirs = os.listdir(workingdir)
            the_dirs = "\n".join(dirs)
            conn.send(the_dirs)

        elif data == 'os':
            conn.send('os is ' + os.name)
            
        conn.send(data)
    conn.close()
    print 'Disconnected by', addr