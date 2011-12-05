from Crypto.Cipher import AES
import random, struct
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
    if not out_filename:
        out_filename = in_filename + '.enc'

    key = '86309lonh6bvcx34'
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)
    #filesize = len(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)
            
            the_string = ''
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)
                the_string += encryptor.encrypt(chunk)
                #outfile.write(encryptor.encrypt(chunk))
            return the_string

def decrypt_file(in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    key = '86309lonh6bvcx34'
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            the_string = ''
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                the_string += decryptor.decrypt(chunk)

            the_string.truncate(origsize)
            return the_string

def compress_file(in_filename, out_filename = None):
    #f = open(in_filename,"r")
    #string = f.read()
    #f.close()
    compr = zlib.compress(in_filename)
    #output = open(out_filename,"w")
    #output.write(compr)
    #output.close()
    return compr
        
def decompress_file(in_string, out_filename = None):
    #f = open(in_filename,"r")
    #string = f.read()
    #f.close()
    decomp = zlib.decompress(in_string)
    #output = open(out_filename,"w")
    #output.write(decomp)
    #output.close()
    return decomp


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
                ENCRYPT = False
                COMPRESS = False
                BINARY = False
                continue
            else:
                print new_dat
                tcpCliSock.close()
                break
        
        else:    
            data = raw_input('Enter a command ')
            
            if data[0:2] == 'ls':
                tcpCliSock.send(data)
                new_dat = tcpCliSock.recv(BUFSIZ)
                print new_dat
                
            elif data[0:2] == 'cd':
                tcpCliSock.send(data)

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
                
                if (ENCRYPT):
                    print 'First fifteen characters of file before encryption', sender[0:15]
                    sender = encrypt_file(file_path)
                    print 'First fifteen characters of file after encryption', sender[0:15]
                
                if (COMPRESS):
                    print 'Length of file before compression:', len(sender)
                    sender = compress_file(sender)
                    print 'Length of file after compression:', len(sender)
                    #print sender
                    
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
                    
                    if COMPRESS:
                        file_data = decompress_file(file_data)
                    
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
                
                #TEST THIS
#                file_paths = []
#                for i in range(0, len(files)):
#                    file_path = files[i]
#                    if (file_path[0] != "\\" and file_path[0] != "/" and file_path[0] != 'C'):
#                        if (os.name == 'nt'):
#                            file_path = os.getcwd() + '\\' + file_path
#                        else:
#                            file_path = os.getcwd() + '/' + file_path
#                    try:
#                        test = os.stat(file_path)
#                    except:
#                        continue
#                    file_paths.append(file_path)
                
                fd = 'mput FILES:' + str(len(files))
                tcpCliSock.send(fd)
                #print files
                
                #now send all files
                for i in range(0, len(files)):
                    tcpCliSock.recv(BUFSIZ)
                    #sender = open(files[i])
                    file_path = files[i]
                    #file_path = file_paths[i] TEST THIS
                    if (file_path[0] != "\\" and file_path[0] != "/" and file_path[0] != 'C'):
                        if (os.name == 'nt'):
                            file_path = os.getcwd() + '\\' + file_path
                        else:
                            file_path = os.getcwd() + '/' + file_path
                            
                    try:        
                        sender = open(file_path).read()
                        
                    except:
                        print 'File located at: ' + file_path + ' not found. Ignoring and moving on.'
                        continue
    
                    file_descriptor = 'put FN:' + get_file_name(file_path)
                    fn = get_file_name(file_path)
                    print file_descriptor
                    tcpCliSock.send(file_descriptor)
                    
                    if (COMPRESS):
                        print 'Length of file:', fn, 'is:', len(sender), 'before compression.'
                        sender = compress_file(sender)
                        print 'Length of file:', fn, 'is:', len(sender), 'after compression.'
                    
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
                    
                    if COMPRESS:
                        f = decompress_file(f)
                    
                    stor.write(f)
                    stor.close()
                    print fn, 'successfully received.'
                
            
            elif data == 'compress':
                tcpCliSock.send(data)
                if COMPRESS:
                    COMPRESS = False
                    print 'Compression disabled'
                else:
                    COMPRESS = True
                    print 'Compression enabled'
                    
            elif data == 'encrypt':
                tcpCliSock.send(data)
                if ENCRYPT:
                    ENCRYPT = False
                    print 'Encryption disabled'
                else:
                    ENCRYPT = True
                    print 'Encryption enabled'
                    
            elif data == 'normal':
                tcpCliSock.send(data)
                COMPRESS = False
                ENCRYPT = False
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