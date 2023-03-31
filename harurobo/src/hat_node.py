#!/usr/bin/env python
import rospy
import actionlib
import time
from harurobo.msg import controller
from harurobo.msg import HandDataAction
from harurobo.msg import HandDataGoal
from harurobo.msg import ManualHand
from std_msgs.msg import Float64MultiArray

ctrl_data = controller()

def controller_callback(data):
    global ctrl_data
    ctrl_data = data
    if ctrl_data.Start and not(ctrl_data.Y or ctrl_data.B or ctrl_data.A):
        init_hat()
    if ctrl_data.X and (ctrl_data.RT or ctrl_data.LT):
        auto.action_client.wait_for_server()
        auto.auto_hat1()
    elif ctrl_data.X:
        manual.manual_controller()

def init_hat():
    auto.action_client.wait_for_server()
    goal = HandDataGoal()
    goal.hand_angle = 0.0 #tojiru
    goal.wrist_angle = 0.0
    goal.shoulder_angle = 144.0 #suityoku [0,163]
    auto.action_client.send_goal(goal)
    auto.action_client.wait_for_result()
    result = auto.action_client.get_result()
    if result.success:
        rospy.loginfo("success : hat intialiation")
    else:
        rospy.loginfo("fail : hat intialiation")

def move(second, speed):
    """指定時間の間バックする"""
    global omni_pub
    rate = rospy.Rate(50)
    start = time.time()
    while(time.time() < start + second):
        omni_power = [1.0 * speed, 1.0 * speed, -1.0 * speed, -1.0 * speed]
        omni_power_for_pub = Float64MultiArray(data = omni_power)
        omni_pub.publish(omni_power_for_pub)
        rate.sleep()
    return True

class Auto_Hat():
    global ctrl_data
    def __init__(self):
        self.action_client = actionlib.SimpleActionClient('auto_hat', HandDataAction)
        self.goal = HandDataGoal()
        self.rate = rospy.Rate(10)
    def auto_hat1(self):
        """帽子を潰す"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto hat")
            return
        self.goal.hand_angle = 0.0
        self.goal.wrist_angle = 20.0 #tekubi wo mageru
        self.goal.shoulder_angle = 20.0 #ude wo orosu
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.auto_hat2()
    def auto_hat2(self):
        """腕を少し上げてバックする"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto hat")
            return
        self.goal.shoulder_angle = 30.0 #ude wo ageru
        self.goal.hand_angle = 90.0 #tume wo ageru
        self.action_client.send_goal(self.goal)
        flag = False
        flag = move(2.0, -0.5)
        while(not flag):
            self.rate.sleep()
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.auto_hat3()
    def auto_hat3(self):
        """腕を地面につけて前進する"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto hat")
            return
        self.goal.shoulder_angle = 0.0 #ude wo orosu
        self.goal.wrist_angle = 54.0
        self.action_client.send_goal(self.goal)
        flag = False
        flag = move(2.0, 0.5)
        while(not flag):
            self.rate.sleep()
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.auto_hat4()
    def auto_hat4(self):
        """爪を下ろして帽子を掴む"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto hat")
            return
        self.goal.hand_angle = 0.0 #tume wo orosu
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.auto_hat5()
    def auto_hat5(self):
        """腕を発射台まで持ち上げる"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto hat")
            return
        self.goal.shoulder_angle = 163.0 #ude wo ageru
        self.goal.wrist_angle = 90.0 - 30.0 - (163.0 - 144.0) #tekubi wo mageru
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            while(1):
                if ctrl_data.y < -0.5:
                    self.auto_hat7()
                    break
                if ctrl_data.y > 0.5:
                    self.auto_hat6()
                    break
                self.rate.sleep()
    def auto_hat6(self):
        """爪を上げて帽子を離し、状態を初期化"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto hat")
            return
        self.goal.hand_angle = 90.0 #tume wo ageru
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            init_hat()
            rospy.loginfo("success : grab hat")
    def auto_hat7(self):
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto hat")
            return
        self.goal.hand_angle = 0.0
        self.goal.wrist_angle = 0.0
        self.goal.shoulder_angle = 20.0
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.auto_hat8()
    def auto_hat8(self):
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto hat")
            return
        self.goal.hand_angle = 90.0
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            init_hat()
            rospy.loginfo("success : separate hat")

class ManualHat():
    global ctrl_data
    def __init__(self):
        self.manual_pub = rospy.Publisher('hat_manual_data', ManualHand, queue_size=10)
    def manual_controller(self):
        manual_data = ManualHand()
        manual_data.finger_vel = ctrl_data.cross_y
        manual_data.wrist_vel = ctrl_data.cross_x
        manual_data.shoulder_vel = ctrl_data.stick_y
        self.manual_pub.publish(manual_data)

if __name__ == "__main__":
    rospy.init_node('sword_A_node')
    ctrl_data_sub = rospy.Subscriber('controller_data', controller, controller_callback, queue_size=10)
    omni_pub = rospy.Publisher('omni_data2', Float64MultiArray, queue_size=1)
    auto = Auto_Hat()
    manual = ManualHat()
    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        pass