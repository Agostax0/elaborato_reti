from socket import *
import os
import time
from packet import *

comands = ["list","get","put"]
path = os.path.dirname(__file__)+"\\download\\" #if the folder doesn't exist
if(not os.path.exists(path)):
    os.mkdir(path)

server_name = 'localhost'
server_port = 1200
client_socket = socket(AF_INET, SOCK_DGRAM)
while True:

    message = input('input the comand: ')
    
    c_packet = packet.from_message(message,200,b'')
    
    print(c_packet)
    
    if(c_packet.comand == "list" or c_packet == "1"): #list comand
        client_socket.sendto(c_packet.encode(),(server_name,server_port))
        s_packet, s_address = client_socket.recvfrom(2048)
        s_packet = decode_packet(s_packet)
        print(s_packet)
    elif(message.__contains__("get") or message.split()[0].__contains__("2")):#get comand
        client_socket.sendto(message.encode(),(server_name,server_port))
        title, s_address = client_socket.recvfrom(2048)
        if(title.decode().__contains__("File not found")):
            print("File not found")
        else:
            file = open(path+title.decode(),'wb')#la creazione file non crea eccezioni
            while True:
                packet, s_address = client_socket.recvfrom(2048)
                if(packet==b''):
                    file.close()
                    break
                else:
                    file.write(packet)
        client_socket.close()
        break
    elif(message.__contains__("put") or message.split()[0].__contains__("3")):#put comand
        title = ""
        message_split = message.split()
        if(len(message_split[1:])>2): #put "test con gli spazi.txt" = ['put','test','con','gli','spazi.txt']
            if(len(message_split[0])==1):
                title = message[2:] #3 ["test con gli spazi.txt"]
            else:
                title = message[4:] #put ["test con gli spazi.txt"]
        else:
            title = message.split()[1] #put [spazi.txt]
        print(title)
        try:
            file = open(path+title ,'rb')
            client_socket.sendto(message.encode(),(server_name,server_port))
            print("sending" + " \"" + title + "\"")
            t0 = time.time()
            while True:
                packet = file.read(2048)
                if(packet==b''):
                    print(title, "has been sent")
                    print("Elapsed time = ", time.time()-t0 , " seconds")
                    client_socket.sendto(b'',(server_name,server_port))
                    #client_socket.sendto("File Sent".encode,(server_name,server_port))
                    file.close()
                    break
                else:
                    client_socket.sendto(packet,(server_name,server_port))
        except Exception:
            print("File not found")
        client_socket.close()
        break
    else:
        client_socket.sendto(message.encode(),(server_name,server_port))
        s_answer, s_address = client_socket.recvfrom(2048)
        #os.system('clear')
        #os.system('cls')
        print(s_answer.decode())