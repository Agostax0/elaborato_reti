FILE_NOT_FOUND_ACKNOWLEDGEMENT = 404
FINISHED_TRANSMISSION_ACKNOWLEDGEMENT = 400
AWAITING_RESPONCE_ACKNOWLEDGEMENT = 100
RECIEVED_ACKNOWLEDGEMENT = 200
class packet:
    def __init__(self,comand,subject,acknowlegde,data):
        self.comand = comand
        self.subject = subject
        self.acknowlegde = acknowlegde
        self.data = data
    @classmethod
    def from_message(self,message,acknowlegde,data):
        try:
            self.comand = message.split()[0]
            self.subject = message[len(self.comand) + 1:]
        except:
            self.comand = "None"
            self.subject = ""
        self.acknowlegde = acknowlegde
        self.data = data
        return self
    @classmethod
    def __str__(self):
        acknowlegde_part = "acknowledge: " + str(len(str(self.acknowlegde))) +" "+ str(self.acknowlegde) + " "
        comand_part = "comand: " + str(len(self.comand)) +" "+ self.comand + " "
        subject_part = "subject: " + str(len(self.subject)) +" " + self.subject + " "
        data_part = "data: " + str(len(self.data)) + " "
        return acknowlegde_part + comand_part + subject_part + data_part
    @classmethod
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