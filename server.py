from socket import *
import os
from packet import *
import time
import datetime
path = os.path.dirname(__file__)+"\\library\\" #if the folder doesn't exist
if(not os.path.exists(path)): #teoricamente la cartella dovrebbe esistere sempre
    os.mkdir(path)  #però non si sa mai, non impatta le performance

commands = {}
commands["list"] = "1 or list ... lists all avaible files"   
commands["get"] = "2 or get [\"name\"] ... downloads the selected file if it exists"
commands["put"] = "3 or put [\"name\"] ... uploads the selected file if it exists"
command_list = []
for command in commands:
    command_list.append(command)
def get_commands_description():
    commands_description = ""
    for tooltip in commands:
        commands_description+=(commands[tooltip]+"\n")
    return commands_description
def get_files():
    files = []
    for file in os.scandir(path):
        files.append(file.name)
    return files

def ls():
    string = ""
    file_id = 1
    for file in get_files():
        string += "["+str(file_id)+"] "+file+ "\t"+ order(os.path.getsize(path+file)) + "\n" 
        file_id += 1
    return string    
def log(client_address,client_packet):
    path = os.path.dirname(__file__)+ "\\"
    log_file = open(path+"log.txt",'a')
    today = "[" + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "] " + str(client_address)+ " " + str(client_packet) + "\n"
    log_file.write(today)
    log_file.close()

server_port = 1200

serversocket = socket(AF_INET, SOCK_DGRAM)

server_address = ('localhost',server_port)

serversocket.bind(server_address)

print('server open on ', server_address)
while True:
    c_packet, client_address = serversocket.recvfrom(BUFFER)
    if(check_packet(c_packet) == False):
        c_packet = packet("None", "None", NEGATIVE_ACKNOWLEDGEMENT, EMPTY_DATA)
    else:
        c_packet = decode_packet(c_packet)
        if(c_packet.ack == POSITIVE_ACKNOWLEDGEMENT):
            log(client_address, c_packet)
        else:#pacchetto corrotto
            c_packet = packet("None", "None", NEGATIVE_ACKNOWLEDGEMENT, EMPTY_DATA)
    if(c_packet.command=="list" or c_packet.command=="1"):
        try:
            s_packet = packet(c_packet.command, c_packet.subject, POSITIVE_ACKNOWLEDGEMENT, ls().encode())
        except:
            s_packet = packet("None", "None", NEGATIVE_ACKNOWLEDGEMENT, EMPTY_DATA)
        toSend = s_packet.encode()
        serversocket.sendto(toSend,client_address)
    elif(c_packet.command=="get" or c_packet.command=="2"):
        try:
            try:
                file_id = int(c_packet.subject)
                files = get_files()
                file_name = files[file_id-1]
            except:
                if(c_packet.subject):
                    file_name = c_packet.subject
            print("client ", client_address," requested ", file_name)
            if(not os.path.exists(path + file_name)): #il server deve informare il client che non ha trovato il file
                print("File not found")
                serversocket.sendto(packet(c_packet.command,c_packet.subject,NEGATIVE_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
            else: 
                f_in = open(path+file_name,'rb')
                serversocket.sendto(packet(c_packet.command,file_name,POSITIVE_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
                t0 = time.time()
                total_delayed = 0
                while True:
                    read = f_in.read(READ)
                    if(read==b''):
                        f_in.close()
                        print("file was sent")
                        size = os.path.getsize(path+file_name)
                        size = str(size).encode()
                        print("file size is:",size.decode())
                        serversocket.sendto(packet(c_packet.command,c_packet.subject,FINISHED_TRANSMISSION_ACKNOWLEDGEMENT,size).encode(),client_address)
                        t1 = time.time() - t0 #- total_delayed
                        serversocket.sendto(packet(c_packet.command,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,(statistics(os.path.getsize(path+file_name),t1)).encode()).encode(),client_address)
                        break
                    else:
                        serversocket.sendto(packet(c_packet.command,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,read).encode(),client_address)
                        total_delayed += delay(1000)
        except: 
            if(len(c_packet.subject)==0):#soggetto del comando non specificato -> file non esistente
                serversocket.sendto(packet(c_packet.command,c_packet.subject,NEGATIVE_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
                print("An error has occured, file name was invalid")
        
    elif (c_packet.command=="put" or c_packet.command=="3"):
        title = c_packet.subject
        print("receiving"+" \"" + title + "\"")
        s_packet = packet(c_packet.command, c_packet.subject, POSITIVE_ACKNOWLEDGEMENT, EMPTY_DATA)
        serversocket.sendto(s_packet.encode(),client_address)
        
        file = open(path+title,'wb')
        t0 = time.time()
        while True:
            file_packet, s_address = serversocket.recvfrom(BUFFER)
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
                        serversocket.sendto(packet(c_packet.command,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,(statistics(os.path.getsize(path+title),t1)).encode()).encode(),client_address)
                        print("file successfully received")
                    else:
                        serversocket.sendto(packet(c_packet.command,c_packet.subject,NEGATIVE_ACKNOWLEDGEMENT,EMPTY_DATA).encode(),client_address)
                        print("File size mismatch")
                    break
                else:
                    file.write(file_packet.data) 
    else:
        if(c_packet.ack==NEGATIVE_ACKNOWLEDGEMENT):
            s_packet = packet("None","None",NEGATIVE_ACKNOWLEDGEMENT,"An error has occoured while receiving".encode()) 
        else:       
            s_packet = packet("None","None",POSITIVE_ACKNOWLEDGEMENT,get_commands_description().encode())
        serversocket.sendto(s_packet.encode(), client_address)