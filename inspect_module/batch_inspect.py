
#设备巡检核心模块：批量巡检华为设备（接口/CPU/内存/VLAN）

import os
import sys
import json
import time
from datetime import datetime

#添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#导入依赖模块
from connect.netmiko_connect import connect_device_group
from config.config_read import SETTINGS

#自定义日志模块
def init_logger():
    import logging
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "inspect.log"), 'a', encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = init_logger()


# 补充巡检子函数
def inspect_interface(device_conn):
    try:
        # 执行接口状态查询命令
        output = device_conn.send_command("display interface brief")
        lines = output.strip().split("\n")[1:]
        abnormal_interfaces = []

        for line in lines:
            if not line.strip():
                continue
                #解析每一行
            parts = line.split()
            if len(parts) < 3:
                continue
            intf_name = parts[0]
            physical_status = parts[1]
            protocol_status = parts[2]
            # 筛选异常接口
            if physical_status.lower() != "up" or protocol_status.lower() != "up":
                abnormal_interfaces.append({
                    "interface": intf_name,
                    "physical_status": physical_status,
                    "protocol_status": protocol_status
                })
        return abnormal_interfaces
    except Exception as e:
        logger.error(f"接口状态巡检失败：{str(e)}")
        return [{"error": f"接口巡检失败：{str(e)}"}]


def inspect_cpu(device_conn, warn_threshold=80):
    try:
        # 执行CPU使用率查询命令
        output = device_conn.send_command("display cpu-usage")
        # 解析CPU使用率
        for line in output.split("\n"):
            if "CPU Usage" in line and "5 sec" in line:
                usage = int(line.split("%")[0].split()[-1])
                is_warn = usage >= warn_threshold
                return usage, is_warn
        return 0, False
    except Exception as e:
        logger.error(f"CPU使用率巡检失败：{str(e)}")
        return -1, True


def inspect_memory(device_conn, warn_threshold=80):
    try:
        # 执行内存使用率查询命令
        output = device_conn.send_command("display memory-usage")
        # 解析内存使用率
        for line in output.split("\n"):
            if "Memory Usage Ratio" in line:
                usage = int(line.split("%")[0].split()[-1])
                is_warn = usage >= warn_threshold
                return usage, is_warn
        return 0, False
    except Exception as e:
        logger.error(f"内存使用率巡检失败：{str(e)}")
        return -1, True


def inspect_vlan(device_conn):
    try:
        # 执行VLAN查询命令
        output = device_conn.send_command("display vlan brief")
        lines = output.strip().split("\n")[1:]
        vlan_list = []

        for line in lines:
            if not line.strip() or "----" in line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            vlan_id = parts[0]
            vlan_name = parts[1] if len(parts) > 1 else "default"
            vlan_list.append({"vlan_id": vlan_id, "vlan_name": vlan_name})
        return vlan_list
    except Exception as e:
        logger.error(f"VLAN状态巡检失败：{str(e)}")
        return [{"error": f"VLAN巡检失败：{str(e)}"}]


#核心巡检逻辑
INSPECT_SETTINGS = SETTINGS.get("inspect", {
    "check_items": ["interface_status", "cpu_usage", "memory_usage", "vlan_status"],
    "warn_threshold": {"cpu_usage": 80, "memory_usage": 80}
})
CHECK_ITEMS = INSPECT_SETTINGS["check_items"]
WARN_THRESHOLD = INSPECT_SETTINGS["warn_threshold"]


def inspect_device(device_conn):
    """单设备全项巡检"""
    inspect_result = {}
    if not device_conn:
        return {"error": "设备连接对象为空"}
    # 接口状态巡检
    if "interface_status" in CHECK_ITEMS:
        inspect_result["interface_status"] = inspect_interface(device_conn)
    # CPU使用率巡检
    if "cpu_usage" in CHECK_ITEMS:
        cpu_threshold = WARN_THRESHOLD.get("cpu_usage", 80)
        cpu_usage, is_warn = inspect_cpu(device_conn, cpu_threshold)
        inspect_result["cpu_usage"] = {"usage": cpu_usage, "is_warn": is_warn}
    # 内存使用率巡检
    if "memory_usage" in CHECK_ITEMS:
        mem_threshold = WARN_THRESHOLD.get("memory_usage", 80)
        mem_usage, is_warn = inspect_memory(device_conn, mem_threshold)
        inspect_result["memory_usage"] = {"usage": mem_usage, "is_warn": is_warn}
    # VLAN状态巡检
    if "vlan_status" in CHECK_ITEMS:
        inspect_result["vlan_status"] = inspect_vlan(device_conn)

    return inspect_result


def batch_inspect(group_name):
    """设备组批量巡检"""
    logger.info(f"开始执行设备组 {group_name} 批量巡检")
    inspect_report = {}
    # 1. 批量连接设备
    try:
        conn_dict = connect_device_group(group_name)
    except KeyError as e:
        logger.error(f"批量巡检失败：{e}")
        return {"error": str(e)}
    # 2. 遍历设备执行巡检
    for device_name, conn in conn_dict.items():
        try:
            if not conn:
                inspect_report[device_name] = {"status": "巡检失败", "reason": "设备未连接"}
                logger.warning(f"设备{device_name}巡检失败：设备未连接")
                continue

            # 执行巡检
            result = inspect_device(conn)
            inspect_report[device_name] = {
                "status": "巡检成功",
                "inspect_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": result
            }

            # 检测预警项
            warn_items = []
            if "cpu_usage" in result and result["cpu_usage"]["is_warn"]:
                warn_items.append(f"CPU使用率超标({result['cpu_usage']['usage']}%)")
            if "memory_usage" in result and result["memory_usage"]["is_warn"]:
                warn_items.append(f"内存使用率超标({result['memory_usage']['usage']}%)")
            if "interface_status" in result and len(result["interface_status"]) > 0:
                warn_items.append(f"异常接口({len(result['interface_status'])}个)")

            if warn_items:
                logger.warning(f"设备{device_name}存在预警：{'; '.join(warn_items)}")
                print(f"【预警】设备{device_name}：{'; '.join(warn_items)}")

        except Exception as e:
            inspect_report[device_name] = {"status": "巡检失败", "reason": str(e)}
            logger.error(f"设备{device_name}巡检失败：{str(e)}")

        finally:
            #连接断开
            if conn:
                conn.disconnect()
                logger.info(f"设备{device_name}巡检完成，已断开连接")

    # 3. 保存巡检报告
    save_inspect_report(inspect_report, group_name)
    logger.info(f"设备组{group_name}批量巡检完成，共巡检{len(inspect_report)}台设备")
    return inspect_report


def save_inspect_report(report, group_name):
    """保存巡检报告至本地"""
    # 创建报告目录（绝对路径）
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inspect_report")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # 生成报告文件名
    report_name = f"{group_name}_inspect_{time.strftime('%Y%m%d%H%M%S')}.json"
    report_path = os.path.join(report_dir, report_name)

    # 保存报告
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        logger.info(f"巡检报告已保存：{report_path}")
    except Exception as e:
        logger.error(f"保存巡检报告失败：{str(e)}")


#测试代码
if __name__ == "__main__":
    try:
        print("===== 开始执行设备组巡检 =====")
        result = batch_inspect("switch_group_a")

        # 打印巡检汇总
        success_count = len([v for v in result.values() if v.get("status") == "巡检成功"])
        fail_count = len(result) - success_count
        print(f"\n===== 巡检汇总 =====")
        print(f"总设备数：{len(result)}")
        print(f"成功巡检：{success_count}台")
        print(f"巡检失败：{fail_count}台")

    except Exception as e:
        logger.error(f"批量巡检程序异常：{str(e)}")
        print(f"程序执行失败：{str(e)}")