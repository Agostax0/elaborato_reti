from socket import *
import os
from packet import *
import datetime
commands = ["list","get","put"]
path = os.path.dirname(__file__)+"\\download\\" #if the folder doesn't exist
if(not os.path.exists(path)):
    os.mkdir(path)

server_name = 'localhost'
server_port = 1200
client_socket = socket(AF_INET, SOCK_DGRAM)
while True:
    output = "["+ str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "] "+ "\n[please input a command] "
    message = input(output)
    c_packet = packet.from_message(message,POSITIVE_ACKNOWLEDGEMENT,EMPTY_DATA)
    if(c_packet.command == "list" or c_packet.command == "1"):
        client_socket.sendto(c_packet.encode(),(server_name,server_port))
        s_packet, s_address = client_socket.recvfrom(2048)
        try:
            s_packet = decode_packet(s_packet)
            if(s_packet.ack==POSITIVE_ACKNOWLEDGEMENT):
                print(s_packet.data.decode())
            else:
                print("Server has denied permission")
        except:
            print("An error has occured, packet has been compromised")
    elif(c_packet.command=="get" or c_packet.command=="2"):
        client_socket.sendto(c_packet.encode(),(server_name,server_port))#il client invia il commando + soggetto
        s_packet, s_address = client_socket.recvfrom(BUFFER)#il server invia che ha trovato + ricevuto la richiesta
        if(check_packet(s_packet)==False):
            print("An error has occured, packet has been compromised")
        else:
            s_packet = decode_packet(s_packet)
            title = s_packet.subject
            if(s_packet.ack==NEGATIVE_ACKNOWLEDGEMENT):#server non ha trovato il file
                print("File not found")
            else:
                if(os.path.exists(path+title)):
                    print("file already exists, substituting with current")
                    os.remove(path+title)
                file = open(path+title,'wb')#la creazione file non crea eccezioni
                while True:
                    file_packet, s_address = client_socket.recvfrom(BUFFER)
                    if(check_packet(file_packet)==False):
                        print("An error has occured, data-packet has been compromised")
                        file.close()
                        break
                    else:
                        file_packet = decode_packet(file_packet)
                        if(file_packet.ack == FINISHED_TRANSMISSION_ACKNOWLEDGEMENT):
                            file.close()
                            
                            if(int(file_packet.data.decode())==os.path.getsize(path+title)):
                                s_packet, s_address = client_socket.recvfrom(BUFFER) #ricezione statistiche
                                if(check_packet(s_packet)==False):
                                    print("An error has occured, server-packet has been compromised")
                                else:
                                    s_packet = decode_packet(s_packet)
                                    print("Successfully received: ", title)
                                    print(s_packet.data.decode())
                            else:
                                print("expected file size: ", order(int(file_packet.data.decode())))
                                print("current file size: ", order(os.path.getsize(path+title)))
                                print("File was not received correctly, file size mismatch")
                            break
                        else:
                            file.write(file_packet.data)
                client_socket.close()
                break
    elif(c_packet.command=="put" or c_packet.command=="3"):
        try:
            if(not os.path.exists(path + c_packet.subject)):
                print("File not found") #Avvisa il client che il file non esiste
            else:
                file = open(path+c_packet.subject ,'rb')
                client_socket.sendto(c_packet.encode(),(server_name,server_port))
                s_packet, s_address = client_socket.recvfrom(BUFFER)
                if(check_packet(s_packet)):
                    if(decode_packet(s_packet).ack==POSITIVE_ACKNOWLEDGEMENT):
                        while True:
                            read = file.read(READ)
                            if(read==b''):
                                file.close()
                                print("file successfully sent")
                                size = os.path.getsize(path+c_packet.subject)
                                size = str(size).encode()
                                client_socket.sendto(packet(c_packet.command,c_packet.subject,FINISHED_TRANSMISSION_ACKNOWLEDGEMENT,size).encode(),s_address)
                                s_packet, s_address = client_socket.recvfrom(BUFFER) #ricezione statistiche o messaggio file non completo
                                
                                if(check_packet(s_packet)==False):
                                    print("An error has occurred, server-packet has been compromised")
                                else:
                                    s_packet = decode_packet(s_packet)
                                    if(s_packet.ack==POSITIVE_ACKNOWLEDGEMENT):
                                        print("Successfully sent: ", c_packet.subject)
                                        print(s_packet.data.decode())
                                    else:
                                        print("File was not received correctly, file size mismatch")
                                break
                            else:
                                client_socket.sendto(packet(c_packet.command,c_packet.subject,POSITIVE_ACKNOWLEDGEMENT,read).encode(),s_address)
                                delay(1000)
                        client_socket.close()
                        break
                    else:
                        print("An error has occured, server has denied permission")       
                else:
                    print("An error has occured, packet has been corrupted")       
        except:
            print("An error has occured, file coudln't be accessed")
    else:
        client_socket.sendto(c_packet.encode(),(server_name,server_port))
        s_packet, s_address = client_socket.recvfrom(BUFFER)
        if(check_packet(s_packet)):
            print(decode_packet(s_packet).data.decode())
        else:
            print("An error has occurred, packet has been compromised")