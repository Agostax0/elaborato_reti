from ctypes import c_double
from socket import *
import os
from packet import *
    
path = os.path.dirname(__file__)+"\\library\\"

comands = {}
comands["list"] = "1 or list ... lists all avaible files"   
comands["get"] = "2 or get [\"name\"] ... downloads the selected file if it exists"
comands["put"] = "3 or put [\"name\"] ... uploads the selected file if it exists"
comand_list = []
for comand in comands:
    comand_list.append(comand)
def get_comands_description():
    comands_description = ""
    for tooltip in comands:
        comands_description+=(comands[tooltip]+"\n")
    return comands_description
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
    c_packet, client_address = serversocket.recvfrom(2048)

    print(c_packet)
    
    c_packet = decode_packet(c_packet)
    
    c_comand = c_packet.comand
    c_subject = c_packet.subject
    c_ack = c_packet.ack
    c_data = c_packet.data
    #print("c_comand:", c_comand)
    #print("c_subj:", c_subject)
    #print("c_ack:", c_ack)
    #print("c_data:", c_data)
    
    if(c_packet.comand=="list" or c_packet.comand=="1"):
        s_packet = packet(c_comand, c_subject, c_ack, ls().encode())
        toSend = s_packet.encode()
        print(toSend)
        serversocket.sendto(toSend,client_address)
    elif(c_comand=="get" or c_comand=="2"):
        try:
            try:
                file_id = int(c_subject)
                print("client referred to the file using its id")
                files = get_files()
                file_name = files[file_id-1]
            except:
                if(c_subject):
                    print("client referred to the file using its name")
                    file_name = c_subject
            print("client ", client_address," requested ", file_name)
            f_in = open(path+file_name,'rb')
            serversocket.sendto(file_name.encode(),client_address)
            while True:
                read = f_in.read(2048)
                if(read==b''):
                    f_in.close()
                    print("file sent")
                    serversocket.sendto(b'',client_address)
                    break
                else:
                    serversocket.sendto(read,client_address)
        except: #il server deve informare il client che non ha trovato il file
            serversocket.sendto("File not found".encode(),client_address)
        
    elif (c_comand=="put" or c_comand=="3"):
        title = c_subject
        print("receiving"+" \"" + title + "\"")
        file = open(path+title,'wb')
        while True:
            packet, client_address = serversocket.recvfrom(2048)
            if(packet==b''):
                file.close()
                print("finished receiving ", title)
                break
            else:
                file.write(packet)
    else:
        serversocket.sendto(get_comands_description().encode(), client_address)