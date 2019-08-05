# mechatronics-2019

 ![MechatronicsGit](https://pbs.twimg.com/profile_images/761612221885452288/dUwJT9It_400x400.jpg)

## About SDSU Mechatronics
San Diego State University Mechatronics is an undergraduate student run organization that strives to bring a multi-disiplinary hands-on education in the field of robotics to students of different educational backgrounds in the San Diego area. Our organization primarily focuses on Autonomous Underwater Vehicles (AUVs) to compete in the international RoboSub competition hosted by RoboNation in San Diego, California. 

![](https://static.wixstatic.com/media/12e446_31a0727b03fb49df80179f01c4a84791~mv2_d_6000_4000_s_4_2.jpg/v1/fill/w_1024,h_689,al_c,q_85,usm_0.66_1.00_0.01/12e446_31a0727b03fb49df80179f01c4a84791~mv2_d_6000_4000_s_4_2.webp)

## This Repository
This repository contains the newly designed software system for the 2019 vehicle Perseverance. The base architecture of the Perserverance 2019 AUV is built off of the MechOS library developed by SDSU Mechatronics. MechOS provides a reliable, fast, and extremely modular BSD socket based communication protocol that allows many of the vehicles systems to be isolated and provides the ability for multimachine communication. This libary promotes a node based system architecute that makes each of the primary systems such as movement control, sensor control, mission tasking, vision, etc. as independent systems all communicating to one another with a topic based publisher/subscriber messaging system.
