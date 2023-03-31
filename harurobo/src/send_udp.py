#!/usr/bin/env python
import socket
import time
import struct
import rospy
from harurobo.msg import RobotData

def callback(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('192.168.0.20', 7777)
#   https://docs.python.org/3/library/struct.html
    message = struct.pack("<fffffffffffffff",
                        data.hat_shoulder_angle,
                        data.sword_A_shoulder_angle,
                        data.sword_B_shoulder_angle,
                        data.launcher_linear_pos,
                        data.launcher_power,
                        data.omni1_power,
                        data.omni2_power,
                        data.omni3_power,
                        data.omni4_power,
                        data.hat_finger_angle,
                        data.sword_A_finger_angle,
                        data.sword_B_finger_angle,
                        data.hat_wrist_angle,
                        data.sword_A_wrist_angle,
                        data.sword_B_wrist_angle)
    sent = sock.sendto(message, server_address)
    sock.close()
    
    
# struct send_data{
#     float hat_shoulder_angle;
#     float sword_A_shoulder_angle;
#     float sword_B_shoulder_angle;
#     float launcher_linear_pos;
#     float launcher_power;
#     float omni1_power;
#     float omni2_power;
#     float omni3_power;
#     float omni4_power;
#     float hat_finger_angle;
#     float sword_A_finger_angle;
#     float sword_B_finger_angle;
#     float hat_wrist_angle;
#     float sword_A_wrist_angle;
#     float sword_B_wrist_angle;
# };

if __name__ == "__main__":
    ros_data = RobotData()
    rospy.init_node('send_udp')
    sub = rospy.Subscriber("ros_data", RobotData, callback, queue_size=10)
    rospy.spin()