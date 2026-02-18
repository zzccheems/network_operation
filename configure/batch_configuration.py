from connect.netmiko_connect import connect_device_group
from config.config_read import DEVICES
import os
from render_tpl import render_tpl
# 根路径
TPL_ROOT = "./template/config_tpl/"

def config_device(device_conn, cmd_list, save_cmd="write memory"):
    """
    单设备配置
    :param device_conn: 设备连接对象
    :param cmd_list: 指令列表
    :param save_cmd: 设备保存指令（不同品牌适配）
    :return: 配置结果（成功/失败）、配置输出
    """
    if not device_conn:
        return "失败", "设备未连接"
    try:
        # 发送配置指令（配置模式）
        output = device_conn.send_config_set(cmd_list)
        # 保存配置
        device_conn.send_command(save_cmd)
        device_conn.exit_config_mode()
        return "成功", output
    except Exception as e:
        return "失败", str(e)

def batch_config(group_name, tpl_name, **tpl_kwargs):
    """
    设备组批量配置
    :param group_name: 设备组名
    :param tpl_name: 模板文件名（如vlan_tpl.txt）
    :param tpl_kwargs: 模板占位符参数
    :return: 批量配置结果字典{设备名: (结果, 输出)}
    """
    # 加载模板并渲染指令
    tpl_path = os.path.join(TPL_ROOT, tpl_name)
    cmd_list = render_tpl(tpl_path, **tpl_kwargs)
    # 批量连接设备
    conn_dict = connect_device_group(group_name)
    # 逐台配置
    result_dict = {}
    for device_name, conn in conn_dict.items():
        # 适配不同品牌保存指令
        save_cmd = "write memory" if "cisco" in DEVICES[group_name][0]["device_type"] else "save"
        result, output = config_device(conn, cmd_list, save_cmd)
        result_dict[device_name] = (result, output)
        # 关闭连接
        if conn:
            conn.disconnect()
    return result_dict

if __name__ == "__main__":
    result = batch_config("switch_group_a", "vlan_tpl.txt", vlan_id=10, vlan_name="IT", interface="GigabitEthernet0/1")
    print(result)