import os
import sys
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入自定义模块
try:
    from config.config_read import DEVICES, SETTINGS
    from configure.render_tpl import render_tpl
    from connect.netmiko_connect import connect_device,connect_device_group
except ImportError as e:
    #导入失败时初始化默认值
    DEVICES = {}
    SETTINGS = {
        "default_username": "admin",
        "default_password": "Huawei@123",
        "timeout": 10,
        "retry": 3
    }
    #定义占位函数
    logger = None


    def connect_device(device_info):
        logger.error(f"netmiko_connect.py 导入失败：{e}，无法连接设备")
        return None


    print(f"【警告】配置模块导入失败：{e}，使用默认配置")


# 初始化日志,主程序日志
def init_batch_logger():
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "batch_config.log"), 'a', encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = init_batch_logger()


def get_devices_by_group(group_name):
    """
    根据设备组名筛选设备
    :param group_name: 设备组名
    :return: 该组下所有设备信息列表
    """
    # 前置参数校验
    if not group_name or not isinstance(group_name, str):
        logger.error(f"设备组名非法：{group_name}（必须为非空字符串）")
        return []

    # 校验DEVICES格式
    if not isinstance(DEVICES, dict):
        logger.error(f"DEVICES配置格式错误，预期字典，实际：{type(DEVICES)}")
        return []

    try:
        #获取设备组的设备列表
        group_devices = DEVICES.get(group_name, [])

        # 二次校验,确保是列表
        if not isinstance(group_devices, list):
            logger.error(f"设备组 {group_name} 的配置格式错误，预期列表，实际：{type(group_devices)}")
            return []

        if not group_devices:
            logger.warning(f"未找到设备组 {group_name} 的任何设备")
            return []

        logger.info(f"筛选出设备组 {group_name} 的设备共 {len(group_devices)} 台")
        return group_devices
    except Exception as e:
        logger.error(f"筛选设备失败：{str(e)}", exc_info=True)
        return []


def send_config(device_conn, config_cmds):
    """
    向设备下发配置
    :param device_conn: 从netmiko_connect获取的连接对象
    :param config_cmds: 配置命令列表
    :return: 下发结果（True/False）
    """
    if not device_conn:
        logger.error("设备连接对象为空，无法下发配置")
        return False
    # 校验配置命令
    if not isinstance(config_cmds, list) or not config_cmds:
        logger.error(f"配置命令格式错误：{config_cmds}（必须为非空列表）")
        return False

    ip = device_conn.host  # 用netmiko连接对象的host属性对应设备IP
    try:
        logger.info(f"开始向设备 {ip} 下发配置，共 {len(config_cmds)} 条命令")
        # 实际下发配置
        output = device_conn.send_config_set(config_cmds)
        logger.info(f"设备 {ip} 配置下发成功，输出：\n{output}")
        return True
    except Exception as e:
        logger.error(f"设备 {ip} 配置下发失败：{str(e)}", exc_info=True)
        return False
    finally:
        #连接关闭
        try:
            device_conn.disconnect()
            logger.info(f"设备 {ip} 连接已关闭")
        except:
            pass


def batch_config(group_name, tpl_name, **tpl_kwargs):
    """
    批量配置核心函数
    :param group_name: 设备组名
    :param tpl_name: 模板文件名
    :param tpl_kwargs: 模板渲染参数
    :return: 批量配置结果字典
    """
    # 初始化结果字典
    result = {
        "total": 0,
        "success": 0,
        "failed": [],
        "group_name": group_name,
        "error": ""
    }

    # 前置参数校验
    if not group_name:
        result["error"] = "设备组名不能为空"
        logger.error(result["error"])
        return result
    if not tpl_name:
        result["error"] = "模板文件名不能为空"
        logger.error(result["error"])
        return result

    # 1. 筛选目标设备
    devices = get_devices_by_group(group_name)
    if not devices:
        result["error"] = f"设备组 {group_name} 无可用设备"
        return result
    result["total"] = len(devices)

    # 2. 渲染配置模板
    try:
        logger.info(f"开始渲染模板 {tpl_name}，参数：{tpl_kwargs}")
        tpl_content = render_tpl(tpl_name, **tpl_kwargs)
        # 将模板内容按行分割为配置命令列表
        config_cmds = [line.strip() for line in tpl_content.split("\n") if line.strip()]

        if not config_cmds:
            raise ValueError("模板渲染后无有效配置命令")
        logger.info(f"模板渲染成功，生成配置命令 {len(config_cmds)} 条")
    except Exception as e:
        result["error"] = f"模板渲染失败：{str(e)}"
        logger.error(result["error"], exc_info=True)
        return result

    # 3. 遍历设备执行配置
    logger.info(f"开始批量配置设备组 {group_name}，共 {len(devices)} 台设备")
    for dev in devices:
        dev_ip = dev.get("ip")
        dev_conn = connect_device(dev)
        if not dev_conn:
            result["failed"].append(dev_ip)
            logger.warning(f"设备 {dev_ip} 加入失败列表")
            continue
        # 下发配置
        if send_config(dev_conn, config_cmds):
            result["success"] += 1
        else:
            result["failed"].append(dev_ip)

    # 4. 输出汇总日志
    logger.info(
        f"批量配置完成 - 设备组：{group_name}，总设备数：{result['total']}，成功：{result['success']}，失败：{len(result['failed'])}")
    if result["failed"]:
        logger.warning(f"失败设备列表：{','.join(result['failed'])}")

    # 5. 返回执行结果
    return result


if __name__ == "__main__":
    # 测试调用
    test_result = batch_config(
        group_name="switch_group_a",
        tpl_name="vlan_tpl.txt",
        vlan_id=100,
        vlan_name="office_network",
        interface="GigabitEthernet0/0/1"
    )
    print("\n【批量配置结果】")
    print(f"设备组：{test_result['group_name']}")
    print(f"总设备数：{test_result['total']}")
    print(f"成功数：{test_result['success']}")
    if test_result["failed"]:
        print(f"失败设备：{','.join(test_result['failed'])}")
    if test_result["error"]:
        print(f"错误信息：{test_result['error']}")