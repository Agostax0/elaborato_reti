from socket import *
import os
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
    if(c_packet.comand == "list" or c_packet.comand == "1"): #list comand
        client_socket.sendto(c_packet.encode(),(server_name,server_port))
        s_packet, s_address = client_socket.recvfrom(2048)
        try:
            s_packet = decode_packet(s_packet)
            if(s_packet.ack==POSITIVE_ACKNOWLEDGEMENT):
                print(s_packet.data.decode())
            else:
                print("Server has denied permission")
        except:
            print("There was an error")
    elif(c_packet.comand=="get" or c_packet.comand=="2"):#get comand
        client_socket.sendto(c_packet.encode(),(server_name,server_port))#il client invia il comando + soggetto
        s_packet, s_address = client_socket.recvfrom(2048)#il server invia che ha trovato + ricevuto la richiesta
        if(check_packet(s_packet)==False):
            print("There was an error, primo pacchetto corrotto")
        else:
            s_packet = decode_packet(s_packet)
            title = s_packet.subject
            if(s_packet.ack==FILE_NOT_FOUND_ACKNOWLEDGEMENT):
                print("File not found")
            else:
                file = open(path+title,'wb')#la creazione file non crea eccezioni
                while True:
                    file_packet, s_address = client_socket.recvfrom(2048)
                    if(check_packet(file_packet)==False):
                        print("There was an error, pacchetto read corrotto")
                        file.close()
                        break
                    else:
                        file_packet = decode_packet(file_packet)
                        #print(file_packet)
                        if(file_packet.ack == FINISHED_TRANSMISSION_ACKNOWLEDGEMENT):
                            file.close()
                            if(int(file_packet.data.decode())==os.path.getsize(path+title)):
                                s_packet, s_address = client_socket.recvfrom(2048) #ricezione statistiche
                                if(check_packet(s_packet)==False):
                                    print("There was an error, primo pacchetto corrotto")
                                else:
                                    s_packet = decode_packet(s_packet)
                                    print("Successfully received: ", title)
                                    print(s_packet.data.decode())
                            else:
                                print("File was not received correctly")
                            break
                        else:
                            file.write(file_packet.data)
            client_socket.close()
            break
    elif(c_packet.comand=="put" or c_packet.comand=="3"):
        print("client:",c_packet)
        try:
            file = open(path+c_packet.subject ,'rb')
            client_socket.sendto(c_packet.encode(),(server_name,server_port))
            s_packet, s_address = client_socket.recvfrom(2048)
            if(check_packet(s_packet)):
                if(decode_packet(s_packet).ack==POSITIVE_ACKNOWLEDGEMENT):
                    while True:
                        read = file.read(1024)
                        if(read==b''):
                            file.close()
                            print("file sent")
                            size = os.path.getsize(path+c_packet.subject)
                            size = str(size).encode()
                            client_socket.sendto(packet(c_packet.comand,c_packet.subject,FINISHED_TRANSMISSION_ACKNOWLEDGEMENT,size).encode(),s_address)
                            s_packet, s_address = client_socket.recvfrom(2048) #ricezione statistiche o messaggio file non completo
                            
                            if(check_packet(s_packet)==False):
                                print("An error has occurred, server packet has been compromised")
                            else:
                                s_packet = decode_packet(s_packet)
                                if(s_packet.ack==POSITIVE_ACKNOWLEDGEMENT):
                                    print("Successfully sent: ", c_packet.subject)
                                    print(s_packet.data.decode())
                                else:
                                    print("File was not received correctly")
                            break
                        else:
                            client_socket.sendto(packet(c_packet.comand,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,read).encode(),s_address)
                    client_socket.close()
                    break
            else:
                print("There was an error, server has denied permission")        
        except:
            print("File not found")
    else:
        client_socket.sendto(c_packet.encode(),(server_name,server_port))
        s_packet, s_address = client_socket.recvfrom(2048)
        if(check_packet(s_packet)):
            print(decode_packet(s_packet).data.decode())
        else:
            print("An error has occurred, packet could be compromised")