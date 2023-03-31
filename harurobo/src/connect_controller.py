#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Joy
from harurobo.msg import controller

ctrl_data = controller()

def joy_callback(joy_msg):
    global ctrl_data
    if joy_msg.buttons[1] == 1:
        ctrl_data.A = True
    else:
        ctrl_data.A = False
    if joy_msg.buttons[2] == 1:
        ctrl_data.B = True
    else:
        ctrl_data.B = False
    if joy_msg.buttons[0] == 1:
        ctrl_data.X = True
    else:
        ctrl_data.X = False
    if joy_msg.buttons[3] == 1:
        ctrl_data.Y = True
    else:
        ctrl_data.Y = False
    if joy_msg.buttons[8] == 1:
        ctrl_data.Back = True
    else:
        ctrl_data.Back = False
    if joy_msg.buttons[9] == 1:
        ctrl_data.Start = True
    else:
        ctrl_data.Start = False
    if joy_msg.buttons[6] == 1:
        ctrl_data.LT = True
    else:
        ctrl_data.LT = False
    if joy_msg.buttons[7] == 1:
        ctrl_data.RT = True
    else:
        ctrl_data.RT = False
    ctrl_data.cross_x = joy_msg.axes[4]
    ctrl_data.cross_y = joy_msg.axes[5]
    ctrl_data.stick_x = joy_msg.axes[0]
    ctrl_data.stick_y = joy_msg.axes[1]
    rospy.loginfo('sub!')

def joy_data():
    global ctrl_data
    joy_sub = rospy.Subscriber('joy', Joy, joy_callback, queue_size=1)
    controller_pub = rospy.Publisher('controller_data', controller, queue_size=1)
    rate = rospy.Rate(50)
    while not rospy.is_shutdown():
            controller_pub.publish(ctrl_data)
            rospy.loginfo('pub!')
            rate.sleep()

if __name__ == "__main__":
    rospy.init_node('connect_controller')
    try:
        joy_data()
    except rospy.ROSInterruptException:
        pass