from Crypto.Cipher import AES
import os,random, struct
import zlib

def encrypt_file(in_filename, out_filename=None, chunksize=64*1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    
    key = '86309lonh6bdcx34'
    
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    key = '86309lonh6bdcx34'
    
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

def compress_file(in_filename):
    f = open(in_filename,"r")
    string = f.read()
    f.close()
    compr = zlib.compress(string)
    output = open(in_filename,"w")
    output.write(compr)
    output.close()
    return compr
        
def decompress_file(in_filename):
    f = open(in_filename,"r")
    string = f.read()
    f.close()
    decomp = zlib.decompress(string)
    output = open(in_filename,"w")
    output.write(decomp)
    output.close()
    return decomp





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
    
    ENCRYPT = False
    COMPRESS = False
    BINARY = False
    
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
                
        elif data == 'compress':
            if COMPRESS:
                COMPRESS = False
                print 'Compression disabled'
            else:
                COMPRESS = True
                print 'Compression enabled'
        
        elif data == 'encrypt':
            if ENCRYPT:
                ENCRYPT = False
                print 'Encryption disabled'
            else:
                ENCRYPT = True
                print 'Encryption enabled'
                            
        elif data == 'normal':
            ENCRYPT = False
            COMPRESS = False
            print 'Compression and Encryption disabled'
            
    conn.close()
    print 'Disconnected by', addr
