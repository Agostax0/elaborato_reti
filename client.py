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
    
    c_packet = packet.from_message(message,AWAITING_RESPONCE_ACKNOWLEDGEMENT,EMPTY_DATA)
    
    print(c_packet.encode())
    
    if(c_packet.comand == "list" or c_packet.comand == "1"): #list comand
        client_socket.sendto(c_packet.encode(),(server_name,server_port))
        s_packet, s_address = client_socket.recvfrom(2048)
        try:
            s_packet = decode_packet(s_packet)
            if(s_packet.ack==POSITIVE_ACKNOWLEDGEMENT):
                print(s_packet.data)
            else:
                print("Server has denied permission")
        except:
            print("There was an error")
    elif(message.__contains__("get") or message.split()[0].__contains__("2")):#get comand
        client_socket.sendto(c_packet.encode(),(server_name,server_port))
        s_packet, s_address = client_socket.recvfrom(2048)
        if(check_packet(s_packet)==False):
            print("There was an error")
        else:
            s_packet = decode_packet(s_packet)
            title = s_packet.subject
            if(s_packet.ack==FILE_NOT_FOUND_ACKNOWLEDGEMENT):
                print("File not found")
            else:
                file = open(path+title,'wb')#la creazione file non crea eccezioni
                client_socket.sendto(packet(s_packet.comand,s_packet.subject,START_TRANSMISSION_ACKNOWLEDGEMENT, EMPTY_DATA).encode(),s_address)
                while True:
                    file_packet, s_address = client_socket.recvfrom(2048)
                    if(check_packet(s_packet)==False):
                        print("There was an error")
                        file.close()
                        break
                    else:
                        file_packet = decode_packet(file_packet)
                        if(file_packet.ack == FINISHED_TRANSMISSION_ACKNOWLEDGEMENT):
                            file.close()
                            break
                        else:
                            file.write(file_packet.data)
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
        client_socket.sendto(c_packet.encode(),(server_name,server_port))
        s_packet, s_address = client_socket.recvfrom(2048)
        if(check_packet(s_packet)):
            print(decode_packet(s_packet).data.decode())
        else:
            print("data was corrupted")