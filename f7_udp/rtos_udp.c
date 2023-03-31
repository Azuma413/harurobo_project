#include <math.h>
#include <rtos_udp.h>
#include <string.h>
static struct receive_data ros_data = { };
static struct send_data f7_data = { };
struct timeval tv;
#define F7_ADDR "192.168.000.020"
#define PC_ADDR "192.168.0.100"
#define F7_PORT 7777
#define PC_PORT 54321

osThreadId controllerTaskHandle;
uint32_t controllerTaskBuffer[512];
osStaticThreadDef_t controllerTaskControlBlock;
void UDPSendReceive(void const *argument);

void UDPDefineTasks() {
	osThreadStaticDef(controllerTask, UDPSendReceive, osPriorityNormal, 0,
			512, controllerTaskBuffer, &controllerTaskControlBlock);
	controllerTaskHandle = osThreadCreate(osThread(controllerTask), NULL);
}

void UDPSendReceive(void const *argument) {
	printf("ender udp task\r\n");
	fd_set reading;
	fd_set sending;
	int rxsock;
	int txsock;
	int iBytesWritten = 0;
	char rxbuf[512]; //最大受信データサイズ
	char txbuf[256]; //最大送信データサイズ
	struct sockaddr_in rxAddr, txAddr;
	rxsock = lwip_socket(AF_INET, SOCK_DGRAM, 0); //udp制御ブロックを作成
	txsock = lwip_socket(AF_INET, SOCK_DGRAM, 0);

	//ソケットを作成
	memset((char*) &rxAddr, 0, sizeof(rxAddr)); //myAddrを0で埋める
	memset((char*) &txAddr, 0, sizeof(txAddr));

	rxAddr.sin_family = AF_INET;
	rxAddr.sin_len = sizeof(rxAddr);
	rxAddr.sin_addr.s_addr = INADDR_ANY; //全てのアドレスから受信
	rxAddr.sin_port = htons(F7_PORT); //マイコンの受信ポート

	txAddr.sin_family = AF_INET;
	txAddr.sin_len = sizeof(txAddr);
	txAddr.sin_addr.s_addr = inet_addr(PC_ADDR); //PC（送信先）のIP
	txAddr.sin_port = htons(PC_PORT); //PC（送信先）のポート

	int err = lwip_bind(rxsock, (struct sockaddr*)&rxAddr, sizeof(rxAddr)); //制御ブロックを送信先のIPとポートに紐づける。
	if (err != 0) {
		printf("UDPController:ERROR \r\n");
	} else {
		printf("UDPController:Socket Opened!\r\n");
	}

	int maxfd = 0;
	int result = 0;
	/*---------test sumple----------*/
	f7_data.omni_x = 0.3f;
	f7_data.omni_y = 0.2f;
	f7_data.hat_shoulder_success = 1;
	f7_data.sword_A_shoulder_success = 0;
	f7_data.sword_B_shoulder_success = 1;
	f7_data.launcher_linear_success = 0;
	/*------------------------*/

	FD_ZERO(&reading); //ディスクリプタ集合の初期化
	FD_ZERO(&sending);
	printf("enter udp loop\r\n");
	while (1) {
		FD_SET(rxsock, &reading); //readingにsock（ディスクリプタ番号）を追加
//		FD_SET(txsock, &sending);
//		if (rxsock > txsock) {
			maxfd = rxsock + 1;
/*		}
		else {
			maxfd = txsock + 1;
		}*/
		memset(&tv, 0, sizeof(tv));
		tv.tv_sec = 0;
		//result = select(maxfd, &reading, &sending, NULL, &tv); //ファイルディスクリプタ―がready状態になるまで1ミリ秒まで待つ。
		result = select(maxfd, &reading, NULL, NULL, &tv);
//		printf("select result: %d\r\n", result);

		if (FD_ISSET(rxsock, &reading)) { //readingの中にsockの値が含まれているか調べる。
			//printf("fd is set\r\n");
			socklen_t n;
			socklen_t len = sizeof(rxAddr);
			n = lwip_recvfrom(rxsock, (char*) rxbuf, sizeof(rxbuf), (int) NULL, (struct sockaddr*) &rxAddr, &len); //rxbufに受信データを格納
			if (n > 0) {
				if (n < sizeof(struct receive_data)) {
					printf("invalid data : \r\n"); //データが欠損しているのでループを送る
					continue;
				}
				struct receive_data *d = (struct receive_data*) &rxbuf; //rxbufの位置にreceive_data構造体を作る。(疑似的にデータが変換される)
				memcpy(&ros_data, d, sizeof(struct receive_data)); //受信データをコピーする
				//printf("omni1:%f\r\nomni2:%f\r\nomni3:%f\r\nomni4:%f\r\n", ros_data.omni1_power, ros_data.omni2_power, ros_data.omni3_power, ros_data.omni4_power); //試験的に出力
			}
		}
		//callback
//		if (FD_ISSET(txsock, &sending)) {
//		printf("set\r\n");
			struct send_data* sd = (struct send_data*)&txbuf; //txbufの位置に重ねてsdを宣言
			memcpy(sd, &f7_data, sizeof(struct send_data)); //送信データをコピーする
			iBytesWritten = lwip_sendto(txsock, (char*)txbuf, sizeof(struct send_data), 0, (struct sockaddr*)&txAddr, sizeof(txAddr));
			//iBytesWritten = lwip_sendto(sock, (char*)"hello world from f7!", 256, 0, (struct sockaddr*)&cAddr, sizeof(cAddr));
			if (iBytesWritten > 0) {
				//printf("success send data\r\n");
				if (iBytesWritten < sizeof(struct send_data)) {
					//printf("send data / invalid\r\n");
				}
				else {
					//printf("send data / complete\r\n");
				}
			}
			else {
				printf("failed : send data\r\n");
			}
//		}
		osDelay(10);
	}
}

struct receive_data UDP_GetROSData(){
	return ros_data;
}

void UDP_SendF7Data(struct send_data *data){
	memcpy(&f7_data, data, sizeof(struct send_data));
}

