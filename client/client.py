from socket import *
import os
path = os.path.dirname(__file__)+"\\download\\" #if the folder doesn't exist
if(not os.path.exists(path)):
    os.mkdir(path)

servername = 'a'
serverport = 1200
clientsocket = socket(AF_INET, SOCK_DGRAM)

while True:
    message = input('input the command: ')
    if(message=='exit'):
        break
    if(message=='ls'):
        clientsocket.sendto("ls".encode(),(servername,serverport))
        s_answer, s_address = clientsocket.recvfrom(2048)
        print(s_answer.decode())
   
    if(message.__contains__('download')):
        clientsocket.sendto(message.encode(),(servername,serverport))
        title, serveraddress = clientsocket.recvfrom(2048)
        file = open(path+title.decode(),'wb')
        while True:
            packet, serveraddress = clientsocket.recvfrom(2048)
            if(packet==b''):
                file.close()
                break
            else:
                file.write(packet)
    
clientsocket.close()
