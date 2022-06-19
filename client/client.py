from socket import *
import os
import sys

comands = ["list","get","put","help"]
path = os.path.dirname(__file__)+"\\download\\" #if the folder doesn't exist
if(not os.path.exists(path)):
    os.mkdir(path)

server_name = 'a'
server_port = 1200
client_socket = socket(AF_INET, SOCK_DGRAM)

while True:
    message = input('input the command: ')
    client_socket.sendto(message.encode(),(server_name,server_port))
    
    if(message.__contains__(comands[0])): #list comand
        s_answer, s_address = client_socket.recvfrom(2048)
        print(s_answer.decode())
   
    if(message.__contains__(comands[1])):#get comand
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
    if(message.__contains__(comands[2])):#put comand
        title = message.split()[1]
        try:
            file = open(path+title ,'rb')
            print("sending ", title)
            while True:
                packet = file.read(2048)
                if(packet==b''):
                    print(title, " sent")
                    client_socket.sendto(b'',(server_name,server_port))
                    file.close()
                    break
                else:
                    client_socket.sendto(packet,(server_name,server_port))
        except:
            print("File not found")
        
    if(message.__contains__(comands[3])):#help comand
        s_answer, s_address = client_socket.recvfrom(2048)
        print(s_answer.decode())
    
    if(message.__contains__('shutdown')):
        client_socket.sendto(message.encode(),(server_name,server_port))
        break
client_socket.close()
sys.exit()