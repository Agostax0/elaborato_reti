FILE_NOT_FOUND_ACKNOWLEDGEMENT = 404
FINISHED_TRANSMISSION_ACKNOWLEDGEMENT = 400
AWAITING_RESPONCE_ACKNOWLEDGEMENT = 100
RECIEVED_ACKNOWLEDGEMENT = 200
class packet:
    def __init__(self,comand,subject,ack,data):
        self.comand = comand
        self.subject = subject
        self.ack = ack
        self.data = data
    @classmethod
    def from_message(self,message,ack,data):
        self.ack = ack
        self.data = data
        try:
            self.comand = message.split()[0]
            self.subject = message[len(self.comand) + 1:]
        except:
            self.comand = "None"
            self.subject = ""
        return self
    @classmethod
    def encode(self):
        temp = packet_str(self)
        return temp.encode() + self.data
def decode_packet(received_packet):
    byte = received_packet.decode()
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
    ret = packet(comand,subject,ack,data)
    return ret
def packet_str(packet):
    acknowledge_part = "ack: " + str(len(str(packet.ack))) +" "+ str(packet.ack) + " "
    comand_part = "comand: " + str(len(packet.comand)) +" "+ packet.comand + " "
    subject_part = "subject: " + str(len(packet.subject)) +" " + packet.subject + " "
    data_part = "data: " + str(len(packet.data)) + " "
    return acknowledge_part + comand_part + subject_part + data_part