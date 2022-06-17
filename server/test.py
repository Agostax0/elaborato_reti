import os
path = os.path.dirname(__file__)+"\\library\\"
def get_files():
    files = []
    for file in os.scandir(path=path):
        files.append(file.name)
    return files
def ls():
    string = ""
    file_id = 1
    for file in get_files():
        string += "["+str(file_id)+"] "+file+"\n" 
        file_id += 1
    return string  
message = input('comand: ')
if(message.__contains__('download')):
        file_id = int(message.replace('download ',''))
        print(file_id)
        files = get_files()
        file = files[file_id-1]
        print(file)
else:
    print(ls())
    