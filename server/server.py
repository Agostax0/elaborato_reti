from socket import *
import os
path = os.path.dirname(__file__)+"\\library\\"
def get_files():
    files = []
    for file in os.scandir(path=path):
        files.append(file.name)
    return files
def ls():
    string = ""
    file_id = 1
    for file in get_files():
        string += "["+str(file_id)+"] "+file+"\n" 
        file_id += 1
    return string    
    

serverport = 1200
serversocket = socket(AF_INET, SOCK_DGRAM)
serversocket.bind(('',serverport))
print("ready to recieve")
while True:
    message, clientAddress = serversocket.recvfrom(2048)
    print("recieved ",message.decode()," from ",clientAddress)
    
    if(message.decode()=='ls'):
       serversocket.sendto(ls().encode(),clientAddress)
    
    if(message.decode().__contains__('download')):
        file_id = int(message.decode().replace('download ',''))
        files = get_files()
        file_name = files[file_id-1]
        print("client ", clientAddress," requesed ", file_name)
        serversocket.sendto(file_name.encode(),clientAddress)
        f_in = open(path+file_name,'rb')
        while True:
            read = f_in.read(2048)
            if(read==b''):
                print("file sent")
                serversocket.sendto(b'',clientAddress)
                break
            else:
                serversocket.sendto(read,clientAddress)
    
    if(message.decode()=='shutdown'):
        serversocket.close()
        exit()

