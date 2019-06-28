'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 03/14/2019
Description: This module is used to obtain the ip/port configurations for
             the mechos nodes that will connect to mechoscore.
'''

class MechOS_Network_Configs:
    '''
    This class will read a txt file formatted with the ip mechoscore is running
    on and the ports for publishers, subscribers, and parameter server clients
    to connect to.
    '''
    def __init__(self, mechos_network_configs_file):
        '''
        Extract the ip address where mechoscore is running and the ports for the
        publishers, subscribers, and parameter server clients to connect to.

        Parameters:
            mechos_network_configs_file: The '.txt' properly formatted containing
                    the mechos network parameters.
        '''
        self.mechos_network_configs_file = mechos_network_configs_file

    def _get_network_parameters(self):
        '''
        Extract the ip address where mechoscore is running and the ports for the
        publishers, subscribers, and parameter server clients to connect to.

        Parameters:
            N/A
        Returns:
            mechos_network_configs: A dictionary containg with the keys
                [ip] --> network ip that mechoscore is running on
                [pub_port] --> port on the ip that the publishers connect to.
                [sub_port] --> port on the ip that the subscribers connect to.
                [param_port] --> The port for the param server to connect to.
        '''
        mechos_network_configs = {}
        file_obj = open(self.mechos_network_configs_file, "r")

        #Line 1 should look like "ip:192.168.1.14"
        mechos_network_configs["param_ip"] = (file_obj.readlines(1)[0])[3:-1]
        mechos_network_configs["ip"] = "tcp://" + mechos_network_configs["param_ip"]
        mechos_network_configs["pub_port"] = (file_obj.readlines(2)[0])[9:-1]
        mechos_network_configs["sub_port"] = (file_obj.readlines(3)[0])[9:-1]
        mechos_network_configs["param_port"] = (file_obj.readlines(4)[0])[11:-1]
        mechos_network_configs["video_port"] = (file_obj.readlines(5)[0])[11:-1]
        mechos_network_configs["param_server_path"] = (file_obj.readlines(6)[0])[19:-1]


        file_obj.close()
        return(mechos_network_configs)

if __name__ == "__main__":
    mechos_network_configs = MechOS_Network_Configs("mechos_network_configs.txt")
    print(mechos_network_configs._get_network_parameters())
