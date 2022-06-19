from socket import *
import os
import sys
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
    
server_port = 1200
serversocket = socket(AF_INET, SOCK_DGRAM)
server_address = ('localhost',server_port)
serversocket.bind(server_address)
print('server open on ', server_address)
while True:
    message, client_address = serversocket.recvfrom(2048)
    print("recieved ", len(message), " bytes from ",client_address, " message: ", message.decode())
    
    if(message.decode()=='ls'):
       serversocket.sendto(ls().encode(),client_address)
    
    if(message.decode().__contains__('download')):
        file_id = int(message.decode().split()[1])
        files = get_files()
        file_name = files[file_id-1]
        print("client ", client_address," requesed ", file_name)
        serversocket.sendto(file_name.encode(),client_address)
        f_in = open(path+file_name,'rb')
        while True:
            read = f_in.read(2048)
            if(read==b''):
                print("file sent")
                serversocket.sendto(b'',client_address)
                break
            else:
                serversocket.sendto(read,client_address)
    
    if(message.decode().__contains__('shutdown')):
        serversocket.close()
        sys.exit()

