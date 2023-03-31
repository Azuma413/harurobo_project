#!/usr/bin/env python
import rospy
import actionlib
from harurobo.msg import controller
from harurobo.msg import HandDataAction
from harurobo.msg import HandDataGoal
from harurobo.msg import ManualHand

state_of_grab_sword = False
ctrl_data = controller()

def controller_callback(data):
    global ctrl_data
    ctrl_data = data
    if ctrl_data.Start and not(ctrl_data.Y or ctrl_data.B or ctrl_data.X):
        init_sword()
    elif ctrl_data.A and (ctrl_data.RT or ctrl_data.LT):
        auto.action_client.wait_for_server()
        global state_of_grab_sword
        if state_of_grab_sword == True:
            auto.release_sword1()
        else:
            if ctrl_data.RT:
                auto.sword_vertical()
            if ctrl_data.LT:
                auto.sword_horizontal()
    elif ctrl_data.A:
        manual.manual_controller()

def init_sword():
    """ペットボトルハンドの状態を初期化する"""
    auto.action_client.wait_for_server()
    goal = HandDataGoal()
    goal.hand_angle = 90 #hiraku
    goal.wrist_angle = 0 #tate
    goal.shoulder_angle = 90 #suityoku
    auto.action_client.send_goal(goal)
    auto.action_client.wait_for_result()
    result = auto.action_client.get_result()
    if result.success:
        rospy.loginfo("success : sword_A intialiation")
    else:
        rospy.loginfo("fail : sword_A intialiation")

class Auto_Sword():
    """ペットボトルハンドを自動で動かす"""
    global ctrl_data
    def __init__(self):
        self.action_client = actionlib.SimpleActionClient('auto_sword_A', HandDataAction)
        self.goal = HandDataGoal()
        self.rate = rospy.Rate(10)
    def sword_vertical(self):
        """ハンドを縦向きにして腕を下ろす"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto sword A")
            return
        self.goal.hand_angle = 90.0
        self.goal.wrist_angle = 0.0
        self.goal.shoulder_angle = 0.0 #ude wo orosu
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.auto_sword2()
    def sword_horizontal(self):
        """ハンドを横向きにして腕を下ろす"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto sword A")
            return
        self.goal.hand_angle = 90.0
        self.goal.wrist_angle = 90.0
        self.goal.shoulder_angle = 0.0 #ude wo orosu
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.auto_sword2()
    def auto_sword2(self):
        """ペットボトルを掴む"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto sword A")
            return
        while(not ctrl_data.A):
            self.rate.sleep() #manual deno iti tyousei
        self.goal.hand_angle = 0.0 #tukamu
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.auto_sword3()
    def auto_sword3(self):
        """腕を上げる"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : auto sword A")
            return
        self.goal.shoulder_angle = 90.0 #ude wo ageru
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            global state_of_grab_sword
            state_of_grab_sword = True
            rospy.loginfo("success : grab sword")
    def release_sword1(self):
        """すでにペットボトルを掴んでいる場合、腕を下ろす"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : release sword A")
            return
        self.goal.shoulder_angle = 20.0 #ude wo orosu
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            self.release_sword2()
    def release_sword2(self):
        """ペットボトルを離して状態を初期化する"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : release sword A")
            return
        self.goal.hand_angle = 90.0 #hiraku
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result = self.action_client.get_result()
        if result.success:
            global state_of_grab_sword
            state_of_grab_sword = False
            init_sword()
            rospy.loginfo("success : grab sword")

class ManualSword():
    """ハンドを手動で操縦する"""
    global ctrl_data
    def __init__(self):
        self.manual_pub = rospy.Publisher('sword_A_manual_data', ManualHand, queue_size=10)
    def manual_controller(self):
        manual_data = ManualHand()
        manual_data.finger_vel = ctrl_data.cross_y
        manual_data.wrist_vel = ctrl_data.cross_x
        manual_data.shoulder_vel = ctrl_data.stick_y
        self.manual_pub.publish(manual_data)

if __name__ == "__main__":
    rospy.init_node('sword_A_node')
    ctrl_data_sub = rospy.Subscriber('controller_data', controller, controller_callback, queue_size=10)
    auto = Auto_Sword()
    manual = ManualSword()
    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        pass