#!/usr/bin/env python
import rospy
import socket
import struct
from harurobo.msg import RobotDataCB

# try:
#    while not rospy.is_shutdown():
#        rospy.Rate(50).sleep()
# except rospy.ROSInterruptException:
#    pass

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

# struct receive_data{
#     float omni_x;
#     float omni_y;
#     int hat_shoulder_success;
#     int sword_A_shoulder_success;
#     int sword_B_shoulder_success;
#     int launcher_linear_success;
# };
if __name__ == "__main__":
    f7_data = RobotDataCB()
    rospy.init_node('receive_udp')
    f7_data_struct = "<ffiiii"
    pub = rospy.Publisher("f7_data", RobotDataCB, queue_size=10)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('0.0.0.0', 54321)
    sock.bind(server_address)
    sock.setblocking(0)

    try:
        while not rospy.is_shutdown():
            while True:
                try:
                    data, address = sock.recvfrom(1024)
                except socket.error:
                    break
                    pass
                else:
                    rospy.loginfo(address)
                    if struct.calcsize(f7_data_struct) == len(data):
                        [omni_x, omni_y, hat_shoulder_success, sword_A_shoulder_success,
                            sword_B_shoulder_success, launcher_linear_success] = struct.unpack(f7_data_struct, data)
                        rospy.loginfo([omni_x, omni_y, hat_shoulder_success, sword_A_shoulder_success,
                            sword_B_shoulder_success, launcher_linear_success])
                        f7_data.omni_x = omni_x
                        f7_data.omni_y = omni_y
                        f7_data.hat_shoulder_success = hat_shoulder_success
                        f7_data.sword_A_shoulder_success = sword_A_shoulder_success
                        f7_data.sword_B_shoulder_success = sword_B_shoulder_success
                        f7_data.launcher_linear_success = launcher_linear_success
                        pub.publish(f7_data)
                    else:
                        rospy.loginfo("received invalid data")
                        rospy.loginfo(len(data))
            rospy.Rate(50).sleep()
    except KeyboardInterrupt:
        # sock.close()
        pass
    finally:
        rospy.loginfo("closing ports...")
        sock.close()
        # if struct.calcsize("<ff")==len(data):
        #     rospy.loginfo(struct.unpack("<ff",data))
        # if struct.calcsize("<BxHfI")==len(data):
        #     rospy.loginfo(struct.unpack("<BxHfI",data))
        # rospy.loginfo()
