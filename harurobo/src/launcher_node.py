#!/usr/bin/env python
import rospy
import actionlib
import math
from harurobo.msg import controller
from harurobo.msg import LaunchDataAction
from harurobo.msg import LaunchDataGoal

ctrl_data = controller()

def controller_callback(data):
    global ctrl_data
    ctrl_data = data
    if ctrl_data.Start and not(ctrl_data.A or ctrl_data.B or ctrl_data.X):
        init_launch()
    elif ctrl_data.Y and (ctrl_data.RT or ctrl_data.LT):
        auto.action_client.wait_for_server()
        auto.launch_callback1()

def init_launch():
    """発射台の状態を初期化する"""
    rospy.loginfo('init_launch')
    launch_angle = 20.0 #tekitou
    linear_pos = degree_to_linearpos(launch_angle)
    auto.action_client.wait_for_server()
    goal = LaunchDataGoal()
    goal.linear_pos = linear_pos
    goal.launch_power = 0
    auto.action_client.send_goal(goal)
    auto.action_client.wait_for_result()
    result0 = auto.action_client.get_result()
    if result0.success:
        rospy.loginfo("success : lanucher intialiation")
    else:
        rospy.loginfo("fail : lanucher intialiation")

def degree_to_linearpos(degree):
    """角度を直動の距離に変換する"""
    base_length = 300 #tekitou
    linear_pos = base_length * math.tan(math.radians(degree))
    return linear_pos

class Auto_Launch():
    """自動で帽子を発射する"""
    global ctrl_data
    def __init__(self):
        self.action_client = actionlib.SimpleActionClient('auto_launch', LaunchDataAction)
        self.goal = LaunchDataGoal()
        if ctrl_data.RT:
            self.far_flag = False
        else:
            self.far_flag = True
    def launch_callback1(self):
        """発射台を４５度に傾け、帽子をセットする"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : lanuch hat")
            return
        lanuch_angle = 45.0 #saidai made katamukete boushi no iti wo kotei
        self.goal.linear_pos = degree_to_linearpos(lanuch_angle)
        self.goal.launch_power = 0
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result1 = self.action_client.get_result()
        if result1.success:
            self.lanuch_callback2()
    def lanuch_callback2(self):
        """発射台を指定角度まで傾ける"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : lanuch hat")
            return
        if self.far_flag:
            lanuch_angle = 30.0 #tekitou
        else:
            lanuch_angle = 20.0
        self.goal.linear_pos = degree_to_linearpos(lanuch_angle)
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result2 = self.action_client.get_result()
        if result2.success:
            self.launch_callback3()
    def launch_callback3(self):
        """帽子を発射する"""
        if ctrl_data.Back:
            rospy.loginfo("interrupt : lanuch hat")
            return
        if self.far_flag:
            self.goal.launch_power = 1.0 #[0,1]
        else:
            self.goal.launch_power = 0.7
        self.action_client.send_goal(self.goal)
        self.action_client.wait_for_result()
        result3 = self.action_client.get_result()
        if result3.success:
            init_launch()
            rospy.loginfo("success : lanuch hat")

if __name__ == "__main__":
    rospy.init_node('launcher_node')
    s = rospy.Subscriber('controller_data', controller, controller_callback, queue_size=10)
    auto = Auto_Launch()
    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        pass