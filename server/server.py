from socket import *
import os
class packet:
    def __init__(self,comand,subject,acknowlegde,data):
        self.comand = comand
        self.subject = subject
        self.acknowlegde = acknowlegde
        self.data = data
    def __str__(self):
        acknowlegde_part = "acknowledge: " + str(len(str(self.acknowlegde))) +" "+ str(self.acknowlegde) + " "
        comand_part = "comand: " + str(len(self.comand)) +" "+ self.comand + " "
        subject_part = "subject: " + str(len(self.subject)) +" " + self.subject + " "
        data_part = "data: " + str(len(self.data)) + " "
        return acknowlegde_part + comand_part + subject_part + data_part
    def encode(self):
        temp = self.__str__()
        return temp.encode() + self.data
def decode_packet(received_packet):
    byte = received_packet.decode()
    splitted = byte.split()
    acknowledge = splitted[2]
    comand = splitted[5]
    subject_part_len = int(splitted[7])
    acknowledge_part_len = len(splitted[0]) + 1 + len(splitted[1]) + 1 + int(splitted[1]) + 1
    comand_part_len = len(splitted[3]) + 1 + len(splitted[4]) + 1 + int(splitted[4]) + 1
    subject_part_start = acknowledge_part_len + comand_part_len + len(splitted[6]) + 1 + len(splitted[7]) + 1
    subject = byte[subject_part_start:subject_part_start+subject_part_len]
    data_part = byte[subject_part_start+subject_part_len + 1:]
    data_splitted = data_part.split()
    data_part_start = len(data_splitted[0]) + 1 + len(data_splitted[1]) + 1
    data = data_part[data_part_start:]
    return packet(comand,subject,acknowledge,data.encode())
    
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
    message, client_address = serversocket.recvfrom(2048)
    message = message.decode()
    
    try:
        c_comand = message.split()[0]
        c_subject = message[len(c_comand)+1:] #prende tutto dopo (primo blocco + " ")
    except:
        if(not c_comand): #se il client invia un comando non vuoto ma un soggetto vuoto
            c_comand = ""   #allora solo il soggetto viene impostato a ""
        c_subject = ""      
    
    if(c_comand=="list" or c_comand=="1"):
        serversocket.sendto(ls().encode(),client_address)
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