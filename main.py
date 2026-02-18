from configure.config_core import batch_config
from inspect.inspect_core import batch_inspect, scheduled_inspect
from web.app import app as flask_app
from log.log_record import logger
import threading
import sys

def show_menu():
    """显示操作菜单"""
    menu = """
    =====================Python网络自动化运维系统=====================
    1. 设备组批量配置
    2. 设备组单次巡检
    3. 启动定时巡检服务
    4. 启动Web可视化界面
    0. 退出系统
    =================================================================
    """
    print(menu)

if __name__ == "__main__":
    logger.info("【系统启动】Python网络自动化运维系统开始运行")
    while True:
        show_menu()
        choice = input("请输入操作编号：").strip()
        if choice == "1":
            group_name = input("请输入设备组名：").strip()
            tpl_name = input("请输入配置模板名：").strip()
            # 简易参数输入，实际可扩展为配置文件读取
            tpl_kwargs = eval(input("请输入模板参数（如{'vlan_id':10, 'vlan_name':'IT'}）："))
            result = batch_config(group_name, tpl_name, **tpl_kwargs)
            print("批量配置结果：", result)
        elif choice == "2":
            group_name = input("请输入设备组名：").strip()
            result = batch_inspect(group_name)
            print("单次巡检结果：", result)
        elif choice == "3":
            # 开启子线程运行定时巡检，避免阻塞主程序
            t = threading.Thread(target=scheduled_inspect, daemon=True)
            t.start()
            logger.info("【定时巡检服务】已启动，按配置间隔执行")
            print("定时巡检服务已启动，日志查看运行状态")
        elif choice == "4":
            # 开启子线程运行Web服务
            t = threading.Thread(target=flask_app.run, kwargs={"host": "0.0.0.0", "port": 5000}, daemon=True)
            t.start()
            logger.info("【Web可视化服务】已启动，访问地址：http://localhost:5000")
            print("Web可视化服务已启动，访问地址：http://localhost:5000")
        elif choice == "0":
            logger.info("【系统退出】Python网络自动化运维系统停止运行")
            print("系统退出，感谢使用！")
            sys.exit(0)
        else:
            print("输入错误，请重新输入！")