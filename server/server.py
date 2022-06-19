from socket import *
import os
import sys
path = os.path.dirname(__file__)+"\\library\\"

comands = ["list","get","put","help"]

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
    
    if(message.decode().__contains__(comands[0])):#list comand
       serversocket.sendto(ls().encode(),client_address)
    
    if(message.decode().__contains__(comands[1])):#get comand
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

    if(message.decode().__contains__(comands[2])):#put comand
        title, client_address = serversocket.recvfrom(2048)
        file = open(path+title.decode(),'wb')
        while True:
            packet, client_address = serversocket.recvfrom(2048)
            if(packet==b''):
                file.close()
                break
            else:
                file.write(packet)
        print("file received")
    
    if(message.decode().__contains__('shutdown')):
        serversocket.close()
        sys.exit()
    
    if(message.decode().__contains__(comands[3])):#help
        comand_description1 = "[list] lists all avaible files" + "\n" + "[get] downloads the file selected" + "\n"
        comand_description2 = "[put] uploads a file" + "\n"
        comand_description = comand_description1 + comand_description2
        serversocket.sendto(comand_description.encode(), client_address)
