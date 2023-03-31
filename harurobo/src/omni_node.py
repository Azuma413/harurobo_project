#!/usr/bin/env python
import rospy
from harurobo.msg import controller
from std_msgs.msg import Float64MultiArray

rotation = 0.0
ideal_vector = [0.0, 0.0]
real_vector = [0.0, 0.0]

def omni_callback(ctrl_data):
    global ideal_vector
    global rotation
    if not(ctrl_data.A or ctrl_data.B or ctrl_data.X or ctrl_data.Y):
        rotation = ctrl_data.cross_x
        ideal_vector = [ctrl_data.stick_y, ctrl_data.stick_x]

def omni_feedback(data):
    global real_vector
    real_vector = [data.data[0], data.data[1]]

def omni_controller():
    global rotation
    global ideal_vector
    global real_vector
    speed = 0.35
    rot_speed = 0.35
    #vector = [2*ideal_vector[0] - real_vector[0], 2*ideal_vector[1] - real_vector[1]]
    vector = ideal_vector
    rot = [-1 * rotation * rot_speed, -1 * rotation * rot_speed, -1 * rotation * rot_speed, -1 * rotation * rot_speed]
    omni_power = [(vector[0] - vector[1])* speed + rot[0], (-1*vector[1] - vector[0])* speed + rot[1], (vector[0] - vector[1])* speed + rot[2], (vector[1] + vector[0])* speed + rot[3]]
    omni_power_forpub = Float64MultiArray(data = omni_power)
    data_pub.publish(omni_power_forpub)

if __name__ == "__main__":
    rospy.init_node('omni_node')
    data_sub1 = rospy.Subscriber('controller_data', controller, omni_callback, queue_size=10)
    data_sub2 = rospy.Subscriber('feedback_data', Float64MultiArray, omni_feedback, queue_size=10)
    data_pub = rospy.Publisher('omni_data', Float64MultiArray, queue_size=10)
    try:
        while not rospy.is_shutdown():
            omni_controller()
            rospy.Rate(50).sleep()
    except rospy.ROSInterruptException:
        pass