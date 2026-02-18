import logging
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException,NetMikoAuthenticationException
import time
from config.config_read import DEVICES
import os
#创建logs目录记录日志
if not os.path.exists("./logs"):
    os.makedirs("./logs")
#配置日志格式和输出方式
logging.basicConfig(
    level=logging.INFO,#记录info,warning和error,critical,不记录debug
    format="%(asctime)s - %(levelname)s - %(message)s",#时间级别内容
    #日志输出位置:同时写入该位置,和控制台
    handlers=[logging.FileHandler("./logs/connect.log",'a', encoding="utf-8"), logging.StreamHandler()]
)
#创建日志实例
logger = logging.getLogger(__name__)



def connect_device(device_info,retry=3):
    """
    单设备连接
    :param device_info: 设备信息字典,来自devices.yaml
    :param retry: 重试次数
    :return: 连接对象
    """
    for i in range(retry):
        try:
            #建立ssh连接,解包字典将参数传递
            conn=ConnectHandler(**device_info)
            #兼容特权模式
            if "secret" in device_info:
                conn.enable()

            success_message=f"[成功]连接设备{device_info['device_name']}({device_info['ip']})"
            logger.info(success_message)
            print(success_message)
            return conn

        except NetMikoTimeoutException:
            error_message=f"[失败]设备{device_info['device_name']}连接超时,第{i+1}次重试"
            logger.warning(error_message)
            print(error_message)
            time.sleep(1)

        except NetMikoAuthenticationException:
            error_message=f"[失败]设备{device_info['device_name']}账号密码错误"
            logger.error(error_message)
            print(error_message)
            break

        except Exception as e:
            error_message=f"[失败]设备{device_info['device_name']}连接异常:{str(e)},第{i+1}次重试"
            logger.error(error_message)
            print(error_message)
            time.sleep(1)
    final_message = f"设备 {device_info['device_name']}({device_info['ip']}) 经{retry}次重试后仍连接失败"
    logger.error(final_message)
    print(f"[最终失败] {final_message}")
    return None

def connect_device_group(group_name):
    """
    设备批量连接
    :param group_name: 设备组名
    :return: 连接字典
    """
    conn_dict={}
    if group_name not in DEVICES:
        error_message=f"设备组{group_name}不存在"
        logger.error(error_message)
        raise KeyError(error_message)

    total_device=len(DEVICES[group_name])
    logger.info(f"开始批量连接设备组 {group_name}，共{total_device}台设备")


    for device in DEVICES[group_name]:
        conn=connect_device(device)
        if conn:
            conn_dict[device['device_name']]=conn
    success_device = len(conn_dict)
    logger.info(f"设备组 {group_name} 批量连接完成：总{total_device}台，成功{success_device}台，失败{total_device - success_device}台")
    print(f"\n[批量连接结果] 设备组{group_name}：总{total_device}台，成功{success_device}台，失败{total_device - success_device}台")
    return conn_dict


if __name__ == "__main__":
    try:
        # 批量连接函数
        conn_dict = connect_device_group("switch_group_a")
        # 后续操作
        for device_name, conn in conn_dict.items():
            # 发送巡检命令
            output = conn.send_command("display version")
            # 记录命令输出
            logger.info(f"{device_name} 版本信息：{output[:300]}")
            # 用完断开连接
            conn.disconnect()
    except KeyError as e:
        # 捕获组名不存在异常
        print(f"调用失败：{e}")