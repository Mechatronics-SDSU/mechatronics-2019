import os
import sys
import pysftp

class File_Transfer():

    def __init__(self, host, username, password):

        self.connection = pysftp.Connection(host=host, username=username,
                                            password=password)

    def receive_file(self, remote_file, local_file):

        try:
            self.connection.get(remote_file, local_file)
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
    local_path_name = str(input("Please specify a file to send"))
    remote_path_name = str(input("Where should I send this file to?"))
    file_transferer.send_file(local_path_name, remote_path_name)
    remote_path_name = str(input("Which file would you now like to receive?"))
    local_path_name = str(input("Where should I copy this file to?"))
    file_transferer.receive_file(remote_path_name, local_path_name)
    file_transferer.kill_connection()

if __name__ == '__main__':
    main()
