# mechatronics-2019
MechOS Code for the 2019 Autonomous Vehicle

 - [x] GUI implemented off the sub
 - [ ] Remote Control Implemented
 - [ ] Mission Commander Ready for Recieving
 - [ ] Robosub competition won

### Remeber
 * in your working directory, to get the GUI to run, please edit **mechos_network_configs.txt**

change 192.168.1.14 to 127.0.0.101

 * The protobufs are precompiled
Do not concern yourself with compiling them

To import:
```python
	import thruster_pb2
	import pid_errors_pb2
	import desired_position_pb2
	import navigation_data_pb2

```
