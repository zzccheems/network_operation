#读取端口限速模板和vlan模板模块

import os

def render_tpl(tpl_name, **tpl_kwargs):
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 模板文件路径
    tpl_dir = os.path.join(current_dir, "config_tpl")
    # 拼接出模板文件的绝对路径
    tpl_path = os.path.join(tpl_dir, tpl_name)

    if not os.path.exists(tpl_path):
        raise FileNotFoundError(f"模板文件 {tpl_path} 不存在")

    with open(tpl_path, 'r', encoding="UTF-8") as f:
        tpl_content = f.read()

    # 渲染模板
    return tpl_content.format(**tpl_kwargs)

if __name__ == '__main__':
    render_tpl( "vlan_tpl.txt",vlan_id=10, vlan_name="net",interface="GigabitEthernet0/0/1")