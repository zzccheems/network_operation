from connect.netmiko_connect import connect_device_group
from config.config_read import SETTINGS
from log.log_record import logger  # 引入日志模块

# 巡检配置
INSPECT_SETTINGS = SETTINGS["inspect"]
CHECK_ITEMS = INSPECT_SETTINGS["check_items"]
WARN_THRESHOLD = INSPECT_SETTINGS["warn_threshold"]

def inspect_device(device_conn):
    """单设备全项巡检"""
    inspect_result = {}
    if "interface_status" in CHECK_ITEMS:
        inspect_result["interface_status"] = inspect_interface(device_conn)
    if "cpu_usage" in CHECK_ITEMS:
        cpu_usage, is_warn = inspect_cpu(device_conn, WARN_THRESHOLD["cpu_usage"])
        inspect_result["cpu_usage"] = {"usage": cpu_usage, "is_warn": is_warn}
    if "memory_usage" in CHECK_ITEMS:
        mem_usage, is_warn = inspect_memory(device_conn, WARN_THRESHOLD["memory_usage"])
        inspect_result["memory_usage"] = {"usage": mem_usage, "is_warn": is_warn}
    if "vlan_status" in CHECK_ITEMS:
        inspect_result["vlan_status"] = inspect_vlan(device_conn)
    return inspect_result

def batch_inspect(group_name):
    """设备组批量巡检"""
    conn_dict = connect_device_group(group_name)
    inspect_report = {}
    for device_name, conn in conn_dict.items():
        if not conn:
            inspect_report[device_name] = {"status": "巡检失败", "reason": "设备未连接"}
            logger.warning(f"设备{device_name}巡检失败：设备未连接")
            continue
        try:
            result = inspect_device(conn)
            inspect_report[device_name] = {"status": "巡检成功", "data": result}
            # 预警判断：存在预警项则记录日志并打印预警
            warn_items = [k for k, v in result.items() if v.get("is_warn") or (isinstance(v, list) and len(v) > 0)]
            if warn_items:
                logger.warning(f"设备{device_name}存在隐患：{warn_items}")
                print(f"【预警】设备{device_name}存在隐患，巡检项：{warn_items}")
        except Exception as e:
            inspect_report[device_name] = {"status": "巡检失败", "reason": str(e)}
            logger.error(f"设备{device_name}巡检失败：{str(e)}")
        finally:
            if conn:
                conn.disconnect()
    # 生成巡检报告并保存
    save_inspect_report(inspect_report, group_name)
    return inspect_report

def save_inspect_report(report, group_name):
    """保存巡检报告至本地（txt/json格式）"""
    import json
    import time
    report_name = f"./inspect_report/{group_name}_inspect_{time.strftime('%Y%m%d%H%M%S')}.json"
    with open(report_name, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    logger.info(f"设备组{group_name}巡检报告已保存：{report_name}")