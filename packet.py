import math
FINISHED_TRANSMISSION_ACKNOWLEDGEMENT = 400
AWAITING_RESPONCE_ACKNOWLEDGEMENT = 100
POSITIVE_ACKNOWLEDGEMENT = 200
NEGATIVE_ACKNOWLEDGEMENT = 300
FILE_NOT_FOUND_ACKNOWLEDGEMENT = NEGATIVE_ACKNOWLEDGEMENT
START_TRANSMISSION_ACKNOWLEDGEMENT = POSITIVE_ACKNOWLEDGEMENT
EMPTY_DATA = b''
class packet:
    def __init__(self,comand,subject,ack,data):
        self.comand = comand
        self.subject = subject
        self.ack = ack
        self.data : bytes = data
    @classmethod
    def from_message(cls,message,ack,data):
        try:
            if(len(message)==0):#se il messaggio è vuoto passa all'except
                raise Exception
            s_comand = message.split()[0]
            s_subject = message[len(s_comand) + 1:]
        except:
            s_comand = "None"
            s_subject = "None"
        return cls(s_comand,s_subject,ack,data)
    
    def __str__(self):
        acknowledge_part = "ack: " + str(len(str(self.ack))) +" "+ str(self.ack) + " "
        comand_part = "comand: " + str(len(self.comand)) +" "+ self.comand + " "
        subject_part = "subject: " + str(len(self.subject)) +" " + self.subject + " "
        data_part = "data: " + str(len(self.data)) + " "
        return acknowledge_part + comand_part + subject_part + data_part

    def encode(self):
        temp = self.__str__()
        return temp.encode() + self.data
    
def decode_packet(received_packet):
    byte = received_packet
    splitted = byte.split()
    ack = splitted[2]
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
    ret = packet(comand.decode(),subject.decode(),int(ack),data)
    return ret
def check_packet(packet):
    try:
        decode_packet(packet)
        return True
    except:
        return False
def statistics(size,time):
    return "Size: " + order(size) + " Time elapsed: " + str(math.floor(time)) + "s Rate: " + order(size/time) + "/s"
def order(measure):
    orders = ["B","KB","MB","GB"]
    order = 0
    val = measure
    while val > 1024:
        val = val / 1024
        order +=1
    return str(math.floor(val)) + orders[order]        
    