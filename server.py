def get_file_name(path):
    name = ''
    for i in range(len(path) - 1, -1, -1):
        if (path[i] == '/' or path[i] == '\\'):
            break
        name += path[i]
    return name[::-1]

# Echo server program
import socket
import os
import re
from math import ceil
from stat import *

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
            f = ''
            done = False
            while (not done):
                dat = conn.recv(buffsize)
                
                if ('>>>~~FILE~~DONE~~<<<' in dat):
                    dat = dat.replace('>>>~~FILE~~DONE~~<<<', '')
                    f.rstrip('>>>~~FILE~~DONE~~<<<')
                    done = True
                
                f += dat
            stor = open(fn,'w')
            stor.write(f)
            stor.close()
            print fn + ' successfully received'
            
        elif data[0:3] == 'get':
            f = data[7:]
            try:
                f_open = open(f).read()
            except:
                print 'Error ' + f + ' not found'
                conn.send('Error ' + f + ' not found')
                continue
            if (f[0] != '\\' and f[0] != '/' and f[0] != 'C'):
                if (os.name == 'nt'):
                    file_path = os.getcwd() + '\\' + f
                else:
                    file_path = os.getcwd() + '/' + f
            else:
                file_path = f
            fd = 'get FN:' + f
            conn.send(fd)
            conn.send(f_open)
            conn.send('>>>~~FILE~~DONE~~<<<')
            
            print f + ' successfully sent'
        
        elif data[0:4] == 'mput':
            fnum = data[11:]
            
            for i in range(0,int(fnum)):
                conn.send('begin transfer number: ' + str(i))
                data = conn.recv(buffsize)
                print data
                pieces = user_split.split(data)
                fn = pieces[0][7:]
                print fn
                if '.' not in fn:
                    fn += '.txt'
                f = ''
                done = False
                while (not done):
                    dat = conn.recv(buffsize)
                    
                    if ('>>>~~FILE~~DONE~~<<<' in dat):
                        dat = dat.replace('>>>~~FILE~~DONE~~<<<', '')
                        #f.rstrip('>>>~~FILE~~DONE~~<<<')
                        done = True
                    
                    f += dat
                stor = open(fn,'w')
                stor.write(f)
                stor.close()
                print fn + ' successfully received'
        
        elif data[0:4] == 'mget':
            files = data[5:]
            if files[-1]=='*':
                file_path= files[:-1]
                if not file_path.strip():
                    file_path = os.getcwd()
                contents = os.listdir(file_path)
                files = []
                for i in range(0,len(contents)):
                    if os.name == 'nt':
                        this_path=file_path + '\\' + contents[i]
                    else:
                        this_path=file_path + '/' + contents[i]
                    mode=os.stat(this_path).st_mode
                    if not S_ISDIR(mode):
                        files.append(this_path)
            else:
                files=files.split()
            fd='mget FILES:' + str(len(files))
            conn.send(fd)
            
            for i in range (0,len(files)):
                conn.recv(buffsize)
                sender = open(files[i])
                file_path = files[i]
                if (file_path[0] != "\\" and file_path[0] != '/' and file_path[0] != 'C'):
                    if (os.name== 'nt'):
                        file_path = os.getcwd() + '\\' + file_path
                    else:
                        file_path = os.getcwd() + '/' + file_path
                try:
                    sender = open(file_path).read()
                except:
                    print 'File located at: ' + file_path + ' not found.  Ignoring \
                    and moving on.'
                
                file_descriptor = 'get FN:' + get_file_name(file_path)
                print file_descriptor
                conn.send(file_descriptor)
                
                conn.send(sender)
                conn.send('>>>~~FILE~~DONE~~<<<')
                
                
                                               
#            try:
#                f_open = open(f).read()
#            except:
#                print 'Error ' + f + ' not found'
#                conn.send('Error ' + f + ' not found')
#                continue
#            if (f[0] != '\\' and f[0] != '/' and f[0] != 'C'):
#                if (os.name == 'nt'):
#                    file_path = os.getcwd() + '\\' + f
#                else:
#                    file_path = os.getcwd() + '/' + f
#            else:
#                file_path = f
#            fd = 'get FN:' + f
#            conn.send(fd)
#            conn.send(f_open)
#            conn.send('>>>~~FILE~~DONE~~<<<')
#            
#            print f + ' successfully sent'
            
    conn.close()
    print 'Disconnected by', addr
