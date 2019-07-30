import os
import sys
import pysftp

class File_Transfer():

    def __init__(self, host, username, password):

        self.connection = pysftp.Connection(host=host, username=username,
                                            password=password)

        self.file_list = self.connection.listdir("test_jsons")
        print(self.file_list)

    def receive_file(self, remote_file, local_file):

        try:
            self.connection.get(remotepath=remote_file, localpath=local_file)
        except Exception as e:
            print("[ERROR]: Couldn't find your file dumbass!!!", e)

    def send_file(self, local_file, remote_file):

        try:
            self.connection.put(local_file, remote_file)
        except Exception as e:
            print("[ERROR]: Couldn't find your file dumbass!!!", e)

    def kill_connection(self):
        self.connection.close()

def main():

    file_transferer = File_Transfer("192.168.1.12", "mechatronics", "Percy2018") #Computer in the trailer
    remote_path = input("Please gimme the file to transfer: ")
    print(remote_path)
    local_path = input("Where should I send it to? ")
    print(local_path)
    file_transferer.receive_file(remote_path, local_path)
    local_path_2 = input("Now what file would you like to send? ")
    print(local_path_2)
    remote_path_2 = input("And where would you like to send it? ")
    print(remote_path_2)
    file_transferer.send_file(local_path_2, remote_path_2)


if __name__ == '__main__':
    main()
