#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备连接模块：基于Netmiko连接华为设备
路径：netmiko_connect.py
"""
import logging
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException
import time
from config.config_read import DEVICES, SETTINGS
import os
import sys

# ========== 基础配置 ==========
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建日志目录（绝对路径）
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "connect.log"), 'a', encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ========== 核心函数 ==========
def connect_device(device_info, retry=3):
    """
    单设备连接（不再依赖 SETTINGS）
    """
    # 直接从 device_info 取，不再用 SETTINGS
    netmiko_params = {
        "device_type": device_info.get("device_type", "huawei_vrpv8"),
        "ip": device_info["ip"],
        "username": device_info.get("username", "admin"),  # 直接用硬编码默认值
        "password": device_info.get("password", "Huawei@123"),
        "port": device_info.get("port", 22),
        "timeout": 10
    }
    netmiko_params = {k: v for k, v in netmiko_params.items() if v is not None}


    # 2. 提取自定义字段（用于日志，不传给Netmiko）
    device_name = device_info.get("device_name", device_info["ip"])
    device_ip = device_info["ip"]

    # 3. 重试连接
    for i in range(retry):
        try:
            # 建立SSH连接
            conn = ConnectHandler(**netmiko_params)

            # 特权模式（如果有secret）
            if "secret" in device_info:
                conn.enable()

            # 日志记录
            success_msg = f"[成功] 连接设备 {device_name} ({device_ip})"
            logger.info(success_msg)
            print(success_msg)
            return conn

        except NetMikoTimeoutException:
            error_msg = f"[失败] 设备 {device_name} ({device_ip}) 连接超时，第{i + 1}次重试"
            logger.warning(error_msg)
            print(error_msg)
            time.sleep(1)

        except NetMikoAuthenticationException:
            error_msg = f"[失败] 设备 {device_name} ({device_ip}) 账号/密码错误"
            logger.error(error_msg)
            print(error_msg)
            break  # 认证错误无需重试

        except Exception as e:
            error_msg = f"[失败] 设备 {device_name} ({device_ip}) 连接异常：{str(e)}，第{i + 1}次重试"
            logger.error(error_msg)
            print(error_msg)
            time.sleep(1)

    # 所有重试失败
    final_msg = f"设备 {device_name} ({device_ip}) 经{retry}次重试后仍连接失败"
    logger.error(final_msg)
    print(f"[最终失败] {final_msg}")
    return None


def connect_device_group(group_name):
    """
    批量连接指定设备组（适配你的嵌套字典格式）
    :param group_name: 设备组名（如 switch_group_a）
    :return: 连接字典 {device_name: conn}
    """
    conn_dict = {}

    # 1. 检查组名是否存在
    if group_name not in DEVICES:
        error_msg = f"设备组 {group_name} 不存在！可用组名：{list(DEVICES.keys())}"
        logger.error(error_msg)
        raise KeyError(error_msg)

    # 2. 获取该组的所有设备
    group_devices = DEVICES[group_name]
    total = len(group_devices)
    logger.info(f"开始批量连接设备组 {group_name}，共{total}台设备")
    print(f"\n===== 开始批量连接设备组 {group_name}（共{total}台）=====")

    # 3. 遍历设备连接
    for device in group_devices:
        conn = connect_device(device, retry=SETTINGS.get("retry", 3))
        if conn:
            conn_dict[device["device_name"]] = conn

    # 4. 统计结果
    success = len(conn_dict)
    fail = total - success
    result_msg = f"设备组 {group_name} 连接完成：总{total}台 | 成功{success}台 | 失败{fail}台"
    logger.info(result_msg)
    print(f"\n===== {result_msg} =====")

    return conn_dict


# ========== 测试代码 ==========
if __name__ == "__main__":
    try:
        # 连接 switch_group_a 组
        conn_dict = connect_device_group("switch_group_a")

        # 遍历连接执行巡检命令
        for dev_name, conn in conn_dict.items():
            try:
                print(f"\n===== 执行 {dev_name} 巡检 =====")
                # 执行华为设备版本查询命令
                output = conn.send_command("display version")
                # 记录前500字符（避免日志过大）
                logger.info(f"{dev_name} 版本信息：{output[:500]}")
                print(f"{dev_name} 版本信息（前500字符）：\n{output[:500]}")
            except Exception as e:
                logger.error(f"{dev_name} 执行命令失败：{str(e)}")
                print(f"{dev_name} 执行命令失败：{str(e)}")
            finally:
                # 确保连接断开
                conn.disconnect()
                logger.info(f"{dev_name} 已断开连接")
                print(f"{dev_name} 已断开连接")

    except KeyError as e:
        print(f"执行失败：{e}")
    except Exception as e:
        logger.error(f"程序异常：{str(e)}")
        print(f"程序异常：{str(e)}")