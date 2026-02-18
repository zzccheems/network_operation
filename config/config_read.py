import yaml
import os
#定义通用yaml读取函数
def read_yaml(file_path):
    #检查配置文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"配置文件{file_path}不存在")
    #安全读取文件
    with open(file_path,'r',encoding="UTF-8") as f:
        #安全加载内容
        data=yaml.safe_load(f)
    #返回配置数据,是字典格式
    return data
#读取具体配置文件生成全局变量给其他模块调用
DEVICES=read_yaml("./config/devices.yaml")
SETTINGS=read_yaml("./config/settings.yaml")