#读取设备配置和系统配置yaml文件模块
import yaml
import os
import sys
# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def read_yaml(file_name):
    """
    读取YAML配置文件,使用绝对路径
    :param file_name: 配置文件名
    :return: 解析后的对象
    """
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接配置文件绝对路径
    full_path = os.path.join(current_dir, file_name)
    # 检查文件是否存在
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"配置文件不存在：{full_path}")
    # 读取并解析YAML文件
    try:
        with open(full_path, 'r', encoding="UTF-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            raise ValueError(f"配置文件 {file_name} 内容为空")
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"解析YAML文件失败：{e}")
#读取设备配置
DEVICES = read_yaml("devices.yaml")
#读取系统配置
SETTINGS = read_yaml("settings.yaml")
