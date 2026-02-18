import os
import sys

# 添加项目根目录到Python路径，解决模块导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入自定义模块（修复路径后的导入）
from config.config_read import DEVICES, SETTINGS
from configure.render_tpl import render_tpl


def get_devices_by_group(group_name):
    """
    根据设备组名筛选设备
    :param group_name: 设备组名（如 "core_switch"、"access_switch"）
    :return: 该组下的所有设备信息列表
    """
    try:
        # 从配置文件中筛选对应组的设备
        group_devices = [dev for dev in DEVICES if dev.get("group") == group_name]
        if not group_devices:
            raise ValueError(f"未找到设备组 {group_name} 的任何设备")
        return group_devices
    except Exception as e:
        print(f"【错误】筛选设备失败：{e}")
        return []


def connect_device(device_info):
    """
    连接网络设备（示例逻辑，可根据实际设备类型扩展）
    :param device_info: 设备信息字典（包含ip、username、password、device_type等）
    :return: 设备连接对象（成功）/None（失败）
    """
    try:
        ip = device_info.get("ip")
        username = device_info.get("username", SETTINGS.get("default_username"))
        password = device_info.get("password", SETTINGS.get("default_password"))
        device_type = device_info.get("device_type", "huawei")

        print(f"【连接设备】{ip} ({device_type})")
        # 这里替换为实际的设备连接逻辑（如使用netmiko/paramiko）
        # 示例：return netmiko.ConnectHandler(**device_info)
        return {"status": "success", "ip": ip}  # 模拟连接成功
    except Exception as e:
        print(f"【连接失败】{device_info.get('ip')}：{e}")
        return None


def send_config(device_conn, config_cmds):
    """
    向设备下发配置
    :param device_conn: 设备连接对象
    :param config_cmds: 配置命令列表
    :return: 下发结果（True/False）
    """
    if not device_conn:
        return False
    try:
        ip = device_conn.get("ip")
        print(f"【下发配置】{ip}：")
        for cmd in config_cmds:
            print(f"  - {cmd}")
        # 这里替换为实际的配置下发逻辑
        # 示例：device_conn.send_config_set(config_cmds)
        return True
    except Exception as e:
        print(f"【配置下发失败】{device_conn.get('ip')}：{e}")
        return False


def batch_config(group_name, tpl_name, **tpl_kwargs):
    """
    批量配置核心函数
    :param group_name: 设备组名
    :param tpl_name: 模板文件名（如 "vlan_tpl.txt"，无需路径）
    :param tpl_kwargs: 模板渲染参数（如 vlan_id=100, vlan_name="office"）
    :return: 批量配置结果字典
    """
    result = {
        "total": 0,
        "success": 0,
        "failed": [],
        "group_name": group_name
    }

    # 1. 筛选目标设备
    devices = get_devices_by_group(group_name)
    if not devices:
        result["error"] = "无可用设备"
        return result
    result["total"] = len(devices)

    # 2. 渲染配置模板（仅传文件名，路径由render_tpl处理）
    try:
        tpl_content = render_tpl(tpl_name, **tpl_kwargs)
        # 将模板内容按行分割为配置命令列表（过滤空行）
        config_cmds = [cmd.strip() for cmd in tpl_content.split("\n") if cmd.strip()]
        if not config_cmds:
            raise ValueError("模板渲染后无有效配置命令")
    except Exception as e:
        result["error"] = f"模板渲染失败：{e}"
        return result

    # 3. 遍历设备执行配置
    for dev in devices:
        # 连接设备
        dev_conn = connect_device(dev)
        if not dev_conn:
            result["failed"].append(dev.get("ip"))
            continue

        # 下发配置
        if send_config(dev_conn, config_cmds):
            result["success"] += 1
        else:
            result["failed"].append(dev.get("ip"))

    # 4. 返回执行结果
    return result


# 测试代码（直接运行该文件时执行）
if __name__ == "__main__":
    # 示例：给core_switch组下发vlan配置
    test_result = batch_config(
        group_name="core_switch",
        tpl_name="vlan_tpl.txt",  # 仅传文件名，路径由render_tpl处理
        vlan_id=100,
        vlan_name="office_network"
    )
    print("\n【批量配置结果】")
    print(f"设备组：{test_result['group_name']}")
    print(f"总设备数：{test_result['total']}")
    print(f"成功数：{test_result['success']}")
    if test_result["failed"]:
        print(f"失败设备：{','.join(test_result['failed'])}")
    if "error" in test_result:
        print(f"错误信息：{test_result['error']}")