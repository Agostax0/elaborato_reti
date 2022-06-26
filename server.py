from socket import *
import os
from packet import *
import time
path = os.path.dirname(__file__)+"\\library\\" #if the folder doesn't exist
if(not os.path.exists(path)): #teoricamente la cartella dovrebbe esistere sempre
    os.mkdir(path)  #però non si sa mai, non impatta le performance

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
        string += "["+str(file_id)+"] "+file+ "\t"+ order(os.path.getsize(path+file)) + "\n" 
        file_id += 1
    return string    
    
server_port = 1200

serversocket = socket(AF_INET, SOCK_DGRAM)

server_address = ('localhost',server_port)

serversocket.bind(server_address)

print('server open on ', server_address)
while True:
    c_packet, client_address = serversocket.recvfrom(2048)
    if(check_packet(c_packet) == False):
        c_packet = packet("None", "None", NEGATIVE_ACKNOWLEDGEMENT, EMPTY_DATA)
        print("client: ", client_address, " sent a corrupted packet")
    else:
        c_packet = decode_packet(c_packet)
        print("client: ", client_address, " sent: ", c_packet)
    if(c_packet.comand=="list" or c_packet.comand=="1"):
        try:
            s_packet = packet(c_packet.comand, c_packet.subject, POSITIVE_ACKNOWLEDGEMENT, ls().encode())
        except:
            s_packet = packet("None", "None", NEGATIVE_ACKNOWLEDGEMENT, EMPTY_DATA)
        toSend = s_packet.encode()
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
            if(not os.path.exists(path+"c_file")): #il server deve informare il client che non ha trovato il file
                print("File not found")
                serversocket.sendto(packet(c_packet.comand,c_packet.subject,FILE_NOT_FOUND_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
            else: 
                f_in = open(path+file_name,'rb')
                serversocket.sendto(packet(c_packet.comand,file_name,START_TRANSMISSION_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
                t0 = time.time()
                while True:
                    read = f_in.read(1024)
                    if(read==b''):
                        f_in.close()
                        print("file successfully sent")
                        size = os.path.getsize(path+file_name)
                        size = str(size).encode()
                        serversocket.sendto(packet(c_packet.comand,c_packet.subject,FINISHED_TRANSMISSION_ACKNOWLEDGEMENT,size).encode(),client_address)
                        t1 = time.time() - t0
                        serversocket.sendto(packet(c_packet.comand,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,(statistics(os.path.getsize(path+file_name),t1)).encode()).encode(),client_address)
                        break
                    else:
                        serversocket.sendto(packet(c_packet.comand,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,read).encode(),client_address)
        except: 
            print("An error has occured")
        
    elif (c_packet.comand=="put" or c_packet.comand=="3"):
        title = c_packet.subject
        print("receiving"+" \"" + title + "\"")
        s_packet = packet(c_packet.comand, c_packet.subject, START_TRANSMISSION_ACKNOWLEDGEMENT, EMPTY_DATA)
        serversocket.sendto(s_packet.encode(),client_address)
        
        file = open(path+title,'wb')
        t0 = time.time()
        while True:
            file_packet, s_address = serversocket.recvfrom(2048)
            if(check_packet(file_packet)==False):
                print("An error has occured while writing")
                file.close()
                break
            else:
                file_packet = decode_packet(file_packet)
                if(file_packet.ack == FINISHED_TRANSMISSION_ACKNOWLEDGEMENT):
                    t1 = time.time() - t0
                    file.close()
                    if(int(file_packet.data.decode())==os.path.getsize(path+title)):
                        serversocket.sendto(packet(c_packet.comand,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,(statistics(os.path.getsize(path+title),t1)).encode()).encode(),client_address)
                        print("file successfully received")
                    else:
                        serversocket.sendto(packet(c_packet.comand,c_packet.subject,NEGATIVE_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
                        print("File size mismatch")
                    break
                else:
                    file.write(file_packet.data) 
    else:
        #print("unrecognised comand", c_packet)
        if(c_packet.ack==NEGATIVE_ACKNOWLEDGEMENT):
            s_packet = packet("None","None",NEGATIVE_ACKNOWLEDGEMENT,"An error has occoured while receiving".encode()) 
        else:       
            s_packet = packet("None","None",POSITIVE_ACKNOWLEDGEMENT,get_comands_description().encode())
        serversocket.sendto(s_packet.encode(), client_address)