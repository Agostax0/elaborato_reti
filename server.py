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

    #print(c_packet)
    if(check_packet(c_packet) == False):
        c_packet = packet("", "", NEGATIVE_ACKNOWLEDGEMENT, EMPTY_DATA)
    else:
        c_packet = decode_packet(c_packet)
    if(c_packet.comand=="list" or c_packet.comand=="1"):
        try:
            #print(ls().encode())
            s_packet = packet(c_packet.comand, c_packet.subject, POSITIVE_ACKNOWLEDGEMENT, ls().encode())
            #print(s_packet.data)
        except:
            s_packet = packet("", "", NEGATIVE_ACKNOWLEDGEMENT, EMPTY_DATA)
        toSend = s_packet.encode()
        #print(toSend)
        serversocket.sendto(toSend,client_address)    
    elif(c_packet.comand=="get" or c_packet.comand=="2"):
        try:
            try:
                file_id = int(c_packet.subject)
                print("client referred to the file using its id")
                files = get_files()
                file_name = files[file_id-1]
            except:
                if(c_packet.subject):
                    print("client referred to the file using its name")
                    file_name = c_packet.subject
            print("client ", client_address," requested ", file_name)
            f_in = open(path+file_name,'rb')
            serversocket.sendto(packet(c_packet.comand,file_name,POSITIVE_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
            while True:
                read = f_in.read(1024)
                
                if(read==b''):
                    f_in.close()
                    print("file sent")
                    serversocket.sendto(packet(c_packet.comand,c_packet.subject,FINISHED_TRANSMISSION_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
                    break
                else:
                    serversocket.sendto(packet(c_packet.comand,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,read).encode(),client_address)
        except: #il server deve informare il client che non ha trovato il file
            serversocket.sendto(packet(c_packet.comand,c_packet.subject,FILE_NOT_FOUND_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
        
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
        if(c_packet.ack==NEGATIVE_ACKNOWLEDGEMENT):
            s_packet = packet("","",NEGATIVE_ACKNOWLEDGEMENT,"There was an error".encode()) 
        else:       
            s_packet = packet("","",POSITIVE_ACKNOWLEDGEMENT,get_comands_description().encode())
        serversocket.sendto(s_packet.encode(), client_address)