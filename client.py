import random, struct
import gzip, zlib

def encrypt_file(input_string):
    key = "29"
    size = len(input_string)
    if (size%2) != 0:
        input_string += " "
    for i in xrange(size/2):
        key += "29"
    input_string = "".join(chr(ord(a)^ord(b))for a,b in zip(input_string,key))
    return input_string
    



#Function inputs a string and outputs a compressed files
def compress_file(input_string, is_binary = False):
    if is_binary:
        if os.name =='nt':
            file_name = os.getcwd() + '\\tempfileftp.gz'
            tempfile = gzip.open(file_name,'wb')
            tempfile.write(input_string)
            tempfile.close()
        else:
            file_name = os.getcwd() + '/tempfileftp.gz'
            tempfile = gzip.open(file_name,'wb')
            tempfile.write(input_string)
            tempfile.close()
    else:
        if os.name =='nt':
            file_name = os.getcwd() + '\\tempfileftp.txt.gz'
            tempfile = gzip.open(file_name ,'wb')
            tempfile.write(input_string)
            tempfile.close()
        else:
            file_name = os.getcwd() + '/tempfileftp.txt.gz'
            tempfile = gzip.open(file_name,'wb')
            tempfile.write(input_string)
            tempfile.close()
        
    return file_name

#Function inputs a compressed file and outputs a string
def decompress_file(in_file):
    tempfile = gzip.open(in_file, 'rb')
    output_string = tempfile.read()
    tempfile.close()
    os.remove(in_file)
    return output_string


def get_file_name(path):
    name = ''
    for i in range(len(path) - 1, -1, -1):
        if (path[i] == '/' or path[i] == '\\'):
            break
        name += path[i]
    return name[::-1]


def grab_domain(m):
    email_re = re.compile('^[\w+\-.]+@[A-Za-z\d\-]+\.(?P<domain>[a-z.]+)+$')
    matches = re.match(email_re, m)
    
    if not matches:
        return False    
    else:
        dom = matches.groups()
        
        domains = ['com', 'edu', 'gov', 'org', 'biz', 'cc', 'us', 'uk', 'co', 'net', 'info', 'me', 'mobi', 'jp', 'co.uk']
        if dom[0] in domains:
            return True
        else:
            return False


#TODO: Remove splitter from client
        #encrypt password before sending
        #have a loop setup so that if we fail login, we can just try again and don't have to reenter host and port info
        #have confirmation for the cd command
        #Maybe remove adding .txt if a file has no extensions
        #In MPUT, in check for wildcard, strip spaces from the end
        #Output successfully sent put files for PUT and MPUT

#Necessary imports 
from socket import *
import os, getpass, math, re
from stat import *

splitter = re.compile('\!@\!')

#connect loop
while 1:

    #by declaring the socket in the loop we can disconnect and reconnect to the
    #same server, we were getting issues otherwise
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    
    HOST = raw_input("Please enter a host name or exit to terminate the client.\n")
    if HOST == 'exit' or HOST == 'quit':
        print 'Goodbye!'
        break

    #Get the actual host
    HOST = gethostbyname(HOST)

    #Prompt user for port
    PORT = int(raw_input("Please enter a port to connect to.\n"))

    #Make address tuple
    ADDR = (HOST, PORT)

    #BUFSIZ is the max buffer size for receiving, arbitrarily chosen
    BUFSIZ = 2048
    new_dat = ''

    #try to connect to this address
    try:
        tcpCliSock.connect(ADDR)
        print 'Connected to: ' + HOST + ' on ' + str(PORT)

        #we now wait to see if the connection was succesful, if it was the server
        #will send a packet with the contents 'pwd' indicating we need login info
        new_dat = tcpCliSock.recv(BUFSIZ)

    #catch an error if we fail and output an error message
    except error as e:
        print "Cannot connect to " + HOST + ' on ' + str(PORT)
        continue

    #data loop
    while 1:

        #pwd is the packet sent that requests the client for their
        #user name and password so we can authenticate them
        if new_dat == 'pwd':

            #server is currently setup only to deal with anonymous users
            user_name = raw_input("Please enter a user name: ")

            #uses the delightful getpass module to easily implement
            #passwords that are entered without echoing (press a key
            #and nothing is printed in the terminal)
            pw = getpass.getpass()
            
            #remember to encrypt pw!
            user_string = 'USER:' + user_name + '!@!PASSWORD:' + pw 

            #Send username and password to server to process
            tcpCliSock.send(user_string)

            #Now, wait for a return packet from the server that indicates if we
            #successfully authenticated and are in the server or if we provided
            #invalid info.
            new_dat = tcpCliSock.recv(BUFSIZ)

            #This packet indicates we successfully authenticated
            #and are now in the server
            if new_dat == 'entry':
                print 'Welcome to the server!'

                #set some bools we will use later for encryption, compression
                #and binary
                ENCRYPT = False
                COMPRESS = False
                BINARY = False
                continue

            #authentication failed, either we used a username other than
            #anonymous or entered an invalid email
            else:

                #print the server's error message, close the socket,
                #and break out of this loop and re-enter the connect loop
                print new_dat
                tcpCliSock.close()
                break

        #If we get any new data other than pwd, we know that we
        #are in the server and can send commands
        else:
            #prompt the user for their FTP command
            data = raw_input('ftp> ')

        #LS and DIR (same implementation)
            if data[0:2] == 'ls' or data[0:3] == 'dir':
                tcpCliSock.send(data)

                #new_dat will have the contents of the ls or dir
                new_dat = tcpCliSock.recv(BUFSIZ)
                print new_dat

        #CD
            elif data[0:2] == 'cd':
                
                #simple command to implement, just send the enter user input
                #command, server handles the rest
                tcpCliSock.send(data)

        #PUT
            elif data[0:3] == 'put':

                #easier to process if command string has no spaces
                file_path = data.replace(' ', '')[3:]

                #make sure the path is ok and can adapt to different OS,
                #however, we don't need to alter the path if it's a root path or
                #an alias to the current path ('/home' or '.' or 'C:\')
                if (file_path[0] != "\\" and file_path[0] != "/" and file_path[0] != 'C' and file_path[0] != '.'):

                    #See if this is a Windows machine, every version of Windows
                    #post Windows 2000 returns 'nt' for os.name
                    if (os.name == 'nt'):
                        file_path = os.getcwd() + '\\' + file_path

                    #otherwise, its likely a Linux Architecture, so use those file paths
                    else:
                        file_path = os.getcwd() + '/' + file_path

                #if the above if was wrong, then the file_path entered in the user
                #command is correct and valid, no changes must be made, can just
                #send it

                #Use a try block here because it allows us to catch opening a
                #non-existant file and throw an error message (and then skip
                #sending the file descriptor)
                try:

                    #If we're in binary mode, open the file in binary mode
                    if (BINARY):
                        sender = open(file_path, 'rb').read()
                        
                    else:
                        sender = open(file_path).read()

                #NOTE: sender now contains the contents of the file we will send,
                #it will always contain the contents of what we will send, even
                #after compression or encryption, or both

                #We've caught an error, likely the file doesn't exist, display a
                #message and continue so no packets are sent
                except:
                    print 'File located at: ' + file_path + ' not found.'
                    continue

                #We use file descriptors to tell the server the name of the file,
                #they resemble: 'put FN:README.txt', the server can grab everything
                #after 'FN:' and use that as the file name it will write to, we
                #always send the file descriptor first
                file_descriptor = 'put FN:' + get_file_name(file_path)
                tcpCliSock.send(file_descriptor)

                #If we're in encrypt mode, run the encryption and print some proof
                #that it worked
                if (ENCRYPT):

                    #encryption proof
                    print 'First fifteen characters of file before encryption', sender[0:15]

                    #simple XOR encryption, also decrypts a file
                    sender = encrypt_file(sender)
                    
                    print 'First fifteen characters of file after encryption', sender[0:15]

                #If we're in compress mode, run the compression (which returns a
                #file name), open the compressed file, and then we will send the
                #contents of the compressed file. We MUST open the compressed
                #file in binary mode on a Windows machine or the compression fails,
                #this is not true for a Linux architecture, however we will always
                #open it in binary mode for safety. Also print messages that
                #prove we compressed the file
                if (COMPRESS):
                    
                    #compression proof
                    print 'Length of file before compression:', len(sender)

                    #Get the name of the compressed file
                    compressed_file_name = compress_file(sender)

                    #open the compressed file in the safe read/binary mode, then
                    #get its contents
                    sender = open(compressed_file_name, 'rb').read()

                    print 'Length of file after compression:', len(sender)

                #Send the contents of the file                    
                tcpCliSock.send(sender)

                #Instead of breaking things into packets, we send the entire file
                #at once, we then send this special string in its own packet, when
                #the server sees that the incoming data contains this string, it
                #removes this string from the data stored in the buffer and writes
                #the entire buffer to a file. The odds of this string appearing
                #in any other file are slim to none
                tcpCliSock.send('>>>~~FILE~~DONE~~<<<')

                #Since our compression algorithm creates a temporary file, we must cleanup
                if (COMPRESS):
                    os.remove(compressed_file_name)
                

        #GET
            elif data[0:3] == 'get':

                #grab the name of the file we want
                file_wanted = data[4:]

                #build the get file descriptor and send it
                fd = 'get FN:' + file_wanted
                tcpCliSock.send(fd)

                #Now, wait for confirmation from the server that this file exists,
                #if it does not, the server will return a packet that begins with:
                #'Error' and then has the error message. This looks for the error
                #packet and prints the message if theres a problem
                new_dat = tcpCliSock.recv(BUFSIZ)
                if (new_dat[0:5] == 'Error'):
                    print new_dat

                #Wasn't an error, so file exists
                else:

                    #We are sent a packet with the incoming file name, we split
                    #the packet into pieces so we have a piece that just has
                    #the file name, then we extract the file name.
                    f_info = splitter.split(new_dat)

                    #Extracts the file name by removing the beginning of the
                    #file descriptor this packet sent
                    fn = f_info[0][7:]

                    #If we were sent a path that has a file name, this will
                    #return us just the file name so we can save a file named
                    #identically.
                    fn = get_file_name(fn)

                    #Will hold file contents
                    file_data = ''

                    #Bool we set when we are done so we can break the loop
                    done = False

                    #While we are not done, get more packets
                    while (not done):

                        #get a packet
                        dat = tcpCliSock.recv(BUFSIZ)

                        #Always check each packet for the end of file packet that
                        #is sent (server also sends them). When it is found,
                        #remove it from the buffer and set done to True to break
                        #out of the loop
                        if '>>>~~FILE~~DONE~~<<<' in dat:

                            #Removes the end of file packet from the buffer
                            dat = dat.replace('>>>~~FILE~~DONE~~<<<', '')

                            #ends the loop
                            done = True

                        #Build file contents
                        file_data += dat

                    #If our filename came without any extensions, add a .txt for
                    #easy opening and compatibility.
                    if '.' not in fn:
                        fn += '.txt'

                    #If the compress falg is set, we need to decompress
                    if COMPRESS:

                        #See what OS we are on and create a temporary file (we
                        #must make a temp file and write the contents of the
                        #buffer to it, then the decompress_file function takes
                        #in the name of that file and decompresses it by opening
                        #it with gzip). We check for the OS to get proper paths
                        if os.name == 'nt':
                            temp_fp = os.getcwd() + '\\temp_file.gzip'
                        else:
                            temp_fp = os.getcwd() + '/temp_file.gzip'

                        #Open the temp file, open in binary mode in case client is
                        #run on a Windows machine
                        temp = open(temp_fp, 'wb')

                        #Write the file data
                        temp.write(file_data)

                        #Close the file to save it
                        temp.close()

                        #Now decompress the file data and store it
                        file_data = decompress_file(temp_fp)

                    #Since the server encrypts and then compresses (in that order),
                    #we must first decompress, and then decrypt (otherwise we decrypt
                    #a compressed file, which causes issues).
                    if ENCRYPT:

                        #We use encrypt_file for decryption as well because our
                        #encryption method uses a simple XOR, which is its own
                        #decryption method
                        file_data = encrypt_file(file_data)

                    #If binary mode is on, write the file in binary mode
                    if BINARY:
                        writer = open(fn, 'wb')

                    #Otherwise, write it normally
                    else:
                        writer = open(fn, 'w')

                    #write the file, close it to save it and print a message
                    #that indicates we got the file successfully
                    writer.write(file_data)
                    writer.close()
                    
                    print fn + ' received successfully'

        #MPUT
            elif data[0:4] == 'mput':

                #Remove the mput part of the command and get the list of files
                #to send
                files = data[5:]

                #Check to see if there was a wildcard passed in, see if it is at
                #the end of a file path or alone
                if files[-1] == '*':

                    #If there is a wild card, get the file path for the directory
                    #we want so we can send the right files, done by just removing
                    #the wildcard
                    file_path = files[:-1]

                    #If the file path is totally empty, the command was: mput *,
                    #which means we want all files from the working directory, so
                    #use that as the path
                    if not file_path.strip():
                        file_path = os.getcwd()

                    #contents is a list of files from the file path
                    contents = os.listdir(file_path)
                    
                    #will store our file names to send
                    files = []

                    #Check to see if an entry is a directory or file
                    for i in range(0, len(contents)):

                        #Check architecture for proper paths
                        if (os.name == 'nt'):

                            #Build path using file_path we made above (made by
                            #removing the wildcard) + the contents of the directory
                            #located at file_path
                            this_path = file_path + '\\' + contents[i]
                        else:
                            this_path = file_path + '/' + contents[i]

                        #Use os.stat to determine if this path contains a directory
                        #or file
                        mode = os.stat(this_path).st_mode

                        #Actual check to see if this path is a directory, if it is
                        #not, we will add it to our list of files
                        if not S_ISDIR(mode):
                            files.append(this_path)

                    #Print statement to summarize what files will be sent
                    print 'We will send files: ',
                    for item in files:
                        print item,

                #Means there is no wildcard, so just split the files string,
                #which is the mput input minus mput
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

                #Send a file descriptor to server, this file descriptor lists
                #the total number of files we will send so server is prepared
                fd = 'mput FILES:' + str(len(files))
                tcpCliSock.send(fd)
                
                #now send all files
                for i in range(0, len(files)):

                    #We need to wait until the server is ready to receive the files
                    #we will send, so we just sit and wait for another packet, the
                    #server will send a packet when it is ready and we can move on
                    tcpCliSock.recv(BUFSIZ)
  
                    file_path = files[i]
                    
                    #file_path = file_paths[i] TEST THIS

                    #Rebuild proper file path for each file in files array
                    if (file_path[0] != "\\" and file_path[0] != "/" and file_path[0] != 'C' and file_path[0] != '.'):

                        #Normal architecture checks
                        if (os.name == 'nt'):
                            file_path = os.getcwd() + '\\' + file_path
                        else:
                            file_path = os.getcwd() + '/' + file_path

                    #Use a try block to open the file so we can determine if a file
                    #exists or not
                    try:

                        #See if we should open it in binary mode
                        if (BINARY):

                            #open in binary mode
                            sender = open(file_path, 'rb').read()

                        #No need to open in binary mode
                        else:
                            sender = open(file_path).read()

                    #Error message for non-existant file
                    except:
                        print 'File located at: ' + file_path + ' not found. Ignoring and moving on.'
                        continue

                    #This is the file descriptor we actually use for each file
                    #we will send. While the first file descriptor sends the
                    #total number of files we will send, this one sends the
                    #name so the server can name it properly. Will be sent for
                    #every file
                    file_descriptor = 'put FN:' + get_file_name(file_path)
                    
                    #fn = get_file_name(file_path)

                    #Send the file descriptor
                    tcpCliSock.send(file_descriptor)

                    #See if we should encrypt, if yes, do so and output proof it
                    #worked
                    if (ENCRYPT):

                        #Encryption proof
                        print 'First fifteen characters of file before encryption', sender[0:15]

                        #Actual encryption method
                        sender = encrypt_file(sender)
                        
                        print 'First fifteen characters of file after encryption', sender[0:15]

                    #See if we should compress, if yes, do so and output proof it
                    #worked
                    if (COMPRESS):
                        #Compression proof
                        print 'Length of file before compression:', len(sender)

                        #compress_file function is setup to return a file name,
                        #so get one
                        compressed_file_name = compress_file(sender)

                        #Open compressed file and copy contents to sender so we
                        #can send them to the server
                        sender = open(compressed_file_name, 'rb').read()
                        
                        print 'Length of file after compression:', len(sender)

                    #Send the contents of each file
                    tcpCliSock.send(sender)

                    #Send end of file packet
                    tcpCliSock.send('>>>~~FILE~~DONE~~<<<')

                    #If compression is on, do temporary file cleanups
                    if COMPRESS:
                        os.remove(compressed_file_name)


        #MGET
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
                    
                    
                    if COMPRESS:
                        if os.name == 'nt':
                            temp_fp = os.getcwd() + '\\temp_file.gzip'
                        else:
                            temp_fp = os.getcwd() + '/temp_file.gzip'
                        temp = open(temp_fp, 'wb')
                        temp.write(f)
                        temp.close()
                        f = decompress_file(temp_fp)
                    if ENCRYPT:
                        f = encrypt_file(f)
                    
                    if BINARY:
                        stor = open(fn, 'wb')
                    else:
                        stor = open(fn, 'wb')
                    stor.write(f)
                    stor.close()
                    print fn, 'successfully received.'
                

        #COMPRESS
            elif data == 'compress':
                tcpCliSock.send(data)
                if COMPRESS:
                    COMPRESS = False
                    print 'Compression disabled'
                else:
                    COMPRESS = True
                    print 'Compression enabled'


        #ENCRYPT   
            elif data == 'encrypt':
                tcpCliSock.send(data)
                if ENCRYPT:
                    ENCRYPT = False
                    print 'Encryption disabled'
                else:
                    ENCRYPT = True
                    print 'Encryption enabled'


        #NORMAL      
            elif data == 'normal':
                tcpCliSock.send(data)
                COMPRESS = False
                ENCRYPT = False
                print 'Encryption and compression disabled'
                
        #BINARY
            elif  data == 'binary':
                tcpCliSock.send(data)
                BINARY = True
                print 'Enabled binary mode'
            
        #ASCII
            elif data == 'ascii':
                tcpCliSock.send(data)
                BINARY = False
                print 'Disabled binary mode'

        #EXIT
            #needs to become quit
            elif data == 'exit' or data == 'quit':
                tcpCliSock.send(data)
                print tcpCliSock.recv(BUFSIZ)
                break
    
    tcpCliSock.close()
