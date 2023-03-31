#!/usr/bin/env python
import rospy
import time
from actionlib import SimpleActionServer
from harurobo.msg import RobotData
from harurobo.msg import RobotDataCB
from std_msgs.msg import Float64MultiArray
from harurobo.msg import HandDataAction
from harurobo.msg import HandDataResult
from harurobo.msg import ManualHand
from harurobo.msg import LaunchDataAction
from harurobo.msg import LaunchDataResult

ROBOT_DATA = RobotData()
ROBOT_CB = RobotDataCB()
#現在の角度を保持するshoulder, wrist, finger
HAT = [0.0, 0.0, 0.0]
SWORD_A = [0.0, 0.0, 0.0]
SWORD_B = [0.0, 0.0, 0.0]
#pos,power
LAUNCHER = [0.0, 0.0]
#launch, hat, sword_A, sword_B
EXECUTE_TIME = [0.0, 0.0, 0.0, 0.0]
launch_result = LaunchDataResult()
hat_result = HandDataResult()
sword_A_result = HandDataResult()
sword_B_result = HandDataResult()
omni_data = Float64MultiArray()
launcher_flag = False
hat_flag = False
sword_A_flag = False
sword_B_flag = False

def f7_callback(data):
    global ROBOT_CB
    ROBOT_CB = data

def manual_hat_cb(data):
    global ROBOT_DATA
    global HAT
    speed = 0.1
    HAT[0] += data.shoulder_vel * speed
    HAT[1] += data.wrist_vel * speed
    HAT[2] += data.finger_vel * speed
    ROBOT_DATA.hat_shoulder_angle = HAT[0]
    ROBOT_DATA.hat_wrist_angle = HAT[1]
    ROBOT_DATA.hat_finger_angle = HAT[2]

def manual_sword_A_cb(data):
    global ROBOT_DATA
    global SWORD_A
    speed = 0.1
    SWORD_A[0] += data.shoulder_vel * speed
    SWORD_A[1] += data.wrist_vel * speed
    SWORD_A[2] += data.finger_vel * speed
    ROBOT_DATA.sword_A_shoulder_angle = SWORD_A[0]
    ROBOT_DATA.sword_A_wrist_angle = SWORD_A[1]
    ROBOT_DATA.sword_A_finger_angle = SWORD_A[2]

def manual_sword_B_cb(data):
    global ROBOT_DATA
    global SWORD_B
    speed = 0.1
    SWORD_B[0] += data.shoulder_vel * speed
    SWORD_B[1] += data.wrist_vel * speed
    SWORD_B[2] += data.finger_vel * speed
    ROBOT_DATA.sword_B_shoulder_angle = SWORD_B[0]
    ROBOT_DATA.sword_B_wrist_angle = SWORD_B[1]
    ROBOT_DATA.sword_B_finger_angle = SWORD_B[2]

def omni_callback(array):
    global ROBOT_DATA
    ROBOT_DATA.omni1_power = array.data[0]
    ROBOT_DATA.omni2_power = array.data[1]
    ROBOT_DATA.omni3_power = array.data[2]
    ROBOT_DATA.omni4_power = array.data[3]

def launch_execute_cb(data):
    rospy.loginfo('called launch_execute_cb')
    global ROBOT_DATA
    global LAUNCHER
    global EXECUTE_TIME
    global launch_result
    global launcher_flag
    EXECUTE_TIME[0] = time.time()
    LAUNCHER[0] = data.linear_pos
    LAUNCHER[1] = data.launch_power
    ROBOT_DATA.launcher_linear_pos = LAUNCHER[0]
    ROBOT_DATA.launcher_power = LAUNCHER[1]
    launcher_flag = True
    while(not launch_result.success):
        rospy.Rate(50).sleep()
    a1.set_succeeded(result = launch_result)
    launch_result.success = False

def hat_execute_cb(data):
    rospy.loginfo('called hat_execute_cb')
    global ROBOT_DATA
    global HAT
    global EXECUTE_TIME
    global hat_result
    global hat_flag
    EXECUTE_TIME[1] = time.time()
    HAT[0] = data.shoulder_angle
    HAT[1] = data.wrist_angle
    HAT[2] = data.hand_angle
    ROBOT_DATA.hat_shoulder_angle = HAT[0]
    ROBOT_DATA.hat_wrist_angle = HAT[1]
    ROBOT_DATA.hat_finger_angle = HAT[2]
    hat_flag = True
    while(not hat_result.success):
        rospy.Rate(50).sleep()
    a2.set_succeeded(result = hat_result)
    hat_result.success = False

def sword_A_execute_cb(data):
    rospy.loginfo('called sword_A_execute_cb')
    global ROBOT_DATA
    global SWORD_A
    global EXECUTE_TIME
    global sword_A_result
    global sword_A_flag
    EXECUTE_TIME[2] = time.time()
    SWORD_A[0] = data.shoulder_angle
    SWORD_A[1] = data.wrist_angle
    SWORD_A[2] = data.hand_angle
    ROBOT_DATA.sword_A_shoulder_angle = SWORD_A[0]
    ROBOT_DATA.sword_A_wrist_angle = SWORD_A[1]
    ROBOT_DATA.sword_A_finger_angle = SWORD_A[2]
    sword_A_flag = True
    while(not sword_A_result.success):
        rospy.Rate(50).sleep()
    a3.set_succeeded(result = sword_A_result)
    sword_A_result.success = False

def sword_B_execute_cb(data):
    rospy.loginfo('called sword_B_execute_cb')
    global ROBOT_DATA
    global SWORD_B
    global EXECUTE_TIME
    global sword_B_result
    global sword_B_flag
    EXECUTE_TIME[3] = time.time()
    SWORD_B[0] = data.shoulder_angle
    SWORD_B[1] = data.wrist_angle
    SWORD_B[2] = data.hand_angle
    ROBOT_DATA.sword_B_shoulder_angle = SWORD_B[0]
    ROBOT_DATA.sword_B_wrist_angle = SWORD_B[1]
    ROBOT_DATA.sword_B_finger_angle = SWORD_B[2]
    sword_B_flag = True
    while(not sword_B_result.success):
        rospy.Rate(50).sleep()
    a4.set_succeeded(result = sword_B_result)
    sword_B_result.success = False

if __name__ == "__main__":
    rospy.init_node('connect_f7')
    f7_pub = rospy.Publisher('ros_data', RobotData, queue_size=10)
    omni_feedack_pub = rospy.Publisher('feedback_data', Float64MultiArray, queue_size=10)
    f7_sub = rospy.Subscriber('f7_data', RobotDataCB, f7_callback, queue_size=10)
    s1 = rospy.Subscriber('hat_manual_data', ManualHand, manual_hat_cb, queue_size=10)
    s2 = rospy.Subscriber('sword_A_manual_data', ManualHand, manual_sword_A_cb, queue_size=10)
    s3 = rospy.Subscriber('sword_B_manual_data', ManualHand, manual_sword_B_cb, queue_size=10)
    s4 = rospy.Subscriber('omni_data', Float64MultiArray, omni_callback, queue_size=10)
    s5 = rospy.Subscriber('omni_data2', Float64MultiArray, omni_callback, queue_size=10)
    a1 = SimpleActionServer('auto_launch', LaunchDataAction, execute_cb=launch_execute_cb)
    a2 = SimpleActionServer('auto_hat', HandDataAction, execute_cb=hat_execute_cb)
    a3 = SimpleActionServer('auto_sword_A', HandDataAction, execute_cb=sword_A_execute_cb)
    a4 = SimpleActionServer('auto_sword_B', HandDataAction, execute_cb=sword_B_execute_cb)
    try:
        while not rospy.is_shutdown():
            omni_data.data = [ROBOT_CB.omni_x, ROBOT_CB.omni_y]
            f7_pub.publish(ROBOT_DATA)
            omni_feedack_pub.publish(omni_data)
            if launcher_flag and (ROBOT_CB.launcher_linear_success or ((time.time() - EXECUTE_TIME[0]) > 3.0)):
                launcher_flag = False
                launch_result.success = True
            if hat_flag and (ROBOT_CB.hat_shoulder_success or ((time.time() - EXECUTE_TIME[1]) > 3.0)):
                hat_flag = False
                hat_result.success = True
            if sword_A_flag and (ROBOT_CB.sword_A_shoulder_success or ((time.time() - EXECUTE_TIME[2]) > 3.0)):
                sword_A_flag = False
                sword_A_result.success = True
            if sword_B_flag and (ROBOT_CB.sword_B_shoulder_success or ((time.time() - EXECUTE_TIME[3]) > 3.0)):
                sword_B_flag = False
                sword_B_result.success = True
            rospy.Rate(50).sleep()
    except rospy.ROSInterruptException:
        pass