from socket import *
import os
import sys

comands = ["list","get","put","help"]
path = os.path.dirname(__file__)+"\\download\\" #if the folder doesn't exist
if(not os.path.exists(path)):
    os.mkdir(path)

servername = 'a'
serverport = 1200
clientsocket = socket(AF_INET, SOCK_DGRAM)

while True:
    message = input('input the command: ')
    clientsocket.sendto(message.encode(),(servername,serverport))
    
    if(message==comands[0]): #list comand
        s_answer, s_address = clientsocket.recvfrom(2048)
        print(s_answer.decode())
   
    if(message.__contains__(comands[1])):#get comand
        title, serveraddress = clientsocket.recvfrom(2048)
        file = open(path+title.decode(),'wb')
        while True:
            packet, serveraddress = clientsocket.recvfrom(2048)
            if(packet==b''):
                file.close()
                break
            else:
                file.write(packet)
    if(message.__contains__(comands[2])):#put comand
        title = message.split()[1]
        clientsocket.sendto(title.encode(),(servername,serverport))
        file = open(path+title ,'rb')
        while True:
            packet = file.read()
            if(packet==b''):
                clientsocket.sendto(packet,(servername,serverport))
                file.close()
                break
            else:
                clientsocket.sendto(packet,(servername,serverport))
    if(message.__contains__(comands[3])):#help comand
        s_answer, serveraddress = clientsocket.recvfrom(2048)
        print(s_answer.decode())
    
    if(message.__contains__('shutdown')):
        clientsocket.sendto(message.encode(),(servername,serverport))
        break
clientsocket.close()
sys.exit()