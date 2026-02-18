#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置读取模块：读取 devices.yaml 和 settings.yaml
路径：config/config_read.py
"""
import yaml
import os
import sys

# 添加项目根目录到Python路径，解决跨目录导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_yaml(file_name):
    """
    读取YAML配置文件（使用绝对路径，避免运行目录问题）
    :param file_name: 配置文件名（如 devices.yaml）
    :return: 解析后的Python对象（字典/列表）
    """
    # 获取当前脚本所在目录（config文件夹）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接配置文件绝对路径
    full_path = os.path.join(current_dir, file_name)

    # 检查文件是否存在
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"配置文件不存在：{full_path}")

    # 读取并解析YAML
    try:
        with open(full_path, 'r', encoding="UTF-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            raise ValueError(f"配置文件 {file_name} 内容为空")
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"解析YAML文件失败：{e}")


# 读取设备配置（适配你的嵌套字典格式）
DEVICES = read_yaml("devices.yaml")

# 可选：读取系统配置（如果有 settings.yaml）
try:
    SETTINGS = read_yaml("settings.yaml")
except FileNotFoundError:
    # 没有则使用默认配置
    SETTINGS = {
        "default_username": "admin",
        "default_password": "Huawei@123",
        "timeout": 10,
        "retry": 3
    }
    print("未找到 settings.yaml，使用默认配置")