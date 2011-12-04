# Echo server program
import socket
import os
import re

HOST = socket.gethostbyname(socket.gethostname())
PORT = 50007
buffsize = 2048
print 'Server hosted on ' + str(HOST) + ' Port ' + str(PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(2)

user_split = re.compile('\!@\!')

while 1:
    print 'Waiting for Connection....'
    conn, addr = s.accept()
    
    conn.send('pwd')
    user = conn.recv(buffsize)
    user_info = user_split.split(user)
    user_name = user_info[0][5:]
    user_pw = user_info[1][9:]
    
    if (user_name != 'anonymous'):
        conn.send('Incorrect Username')
        print str(addr) + ' tried to connect with invalid user name: ' + user_name
        conn.close()
        continue
    else:
        if (user_pw != 'hjc1710@gmail.com'):
            conn.send('Incorrect Password')
            print str(addr) + ' tried to connect with invalid password.'
            conn.close()
            continue
        else:
            conn.send('entry')
    
    print 'Connected by', addr
    workingdir = os.curdir
    
    while 1:
        data = conn.recv(buffsize)

        if data == 'exit':
            break
        elif not data:
            break
        elif data == 'ls':
            dirs = os.listdir(os.getcwd())
            the_dirs = "\n".join(dirs)
            conn.send(the_dirs)

        elif data == 'os':
            conn.send('os is ' + os.name)
        
        elif data[0:2] == 'cd':
            print data[3:]
            os.chdir(data[3:])
        
        elif data[0:3] == 'put':
            pieces = user_split.split(data)
            print pieces
            fn = pieces[0][7:]
            if '.' not in fn:
                fn += '.txt'
            packets = pieces[1][8:]
            f = ''
            for i in range(0,int(packets)):
                f += conn.recv(buffsize)
            stor = open(fn,'w')
            stor.write(f)
            stor.close()
            print fn + ' successfully received'
            
        elif data[0:3] == 'get':
            
            
            print fn + ' successfully sent'
        #conn.send(data)
    conn.close()
    print 'Disconnected by', addr
