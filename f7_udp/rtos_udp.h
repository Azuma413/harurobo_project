#ifndef UDPCONTROLLER_H_
#define UDPCONTROLLER_H_


#include "lwip.h"
#include "lwip/sockets.h"

struct receive_data {
	float hat_shoulder_angle;
	float sword_A_shoulder_angle;
	float sword_B_shoulder_angle;
	float launcher_linear_pos;
	float launcher_power;
	float omni1_power;
	float omni2_power;
	float omni3_power;
	float omni4_power;
	float hat_finger_angle;
	float sword_A_finger_angle;
	float sword_B_finger_angle;
	float hat_wrist_angle;
	float sword_A_wrist_angle;
	float sword_B_wrist_angle;
};

struct send_data {
	float omni_x;
	float omni_y;
	int hat_shoulder_success;
	int sword_A_shoulder_success;
	int sword_B_shoulder_success;
	int launcher_linear_success;
};
struct receive_data UDP_GetROSData();
void UDP_SendF7Data(struct send_data*);
void UDPDefineTasks();
#endif /* UDPCONTROLLER_H_ */
