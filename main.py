#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python网络自动化运维系统 - 主程序入口
路径：network_operation/main.py
"""
import os
import sys
import threading
import time
import ast  # 提前导入，避免局部导入报错

# ========== 核心修复1：添加项目根目录到Python路径 ==========
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== 核心修复2：适配实际项目架构的导入 ==========
# 1. 批量配置模块（实际文件：configure/batch_configuration.py）
try:
    from configure.batch_configuration import batch_config
except ImportError as e:
    logger = None  # 先占位，避免日志未初始化时报错


    # 定义占位函数，避免程序崩溃
    def batch_config(group_name, tpl_name, **kwargs):
        return {
            "error": f"批量配置模块导入失败：{str(e)}，请检查 configure/batch_configuration.py"
        }

# 2. 巡检模块（兼容 batch_inspect.py / inspect_core.py）
try:
    from inspect_module.batch_inspect import batch_inspect
except ImportError:
    try:
        from inspect_module.inspect_core import batch_inspect
    except ImportError as e:
        # 定义占位函数
        def batch_inspect(group_name):
            return {
                "error": f"巡检模块导入失败：{str(e)}，请检查 inspect_module 下的文件"
            }


# ========== 核心修复3：统一日志模块 ==========
def init_main_logger():
    """初始化全局日志（主程序+巡检共用）"""
    import logging
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "main.log"), 'a', encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


# 全局日志实例
logger = init_main_logger()


# ========== 核心修复4：定时巡检函数 ==========
def scheduled_inspect(interval=3600, group_names=["switch_group_a", "router_group_b"]):
    """定时巡检服务（使用全局 logger）"""
    logger.info(f"定时巡检服务启动，间隔{interval}秒，巡检组：{group_names}")
    while True:
        try:
            logger.info("===== 开始定时巡检 =====")
            for group in group_names:
                logger.info(f"开始巡检设备组：{group}")
                batch_inspect(group)
                logger.info(f"设备组{group}巡检完成")
            logger.info("===== 定时巡检结束 =====")
            time.sleep(interval)
        except Exception as e:
            logger.error(f"定时巡检异常：{str(e)}")
            time.sleep(60)  # 异常时暂停1分钟再重试


# ========== 核心修复5：完整的Web服务逻辑（修复空函数问题） ==========
# 优先导入自定义 Web 模块
try:
    from web.app import app as flask_app

    logger.info("成功导入自定义Web模块（web/app.py）")
except ImportError:
    logger.warning("未找到自定义Web模块，启用内置简易Web服务")


    # 完整的备用Web服务实现（不再是空函数）
    def init_flask_app():
        """初始化简易Web服务"""
        try:
            from flask import Flask, jsonify
            app = Flask(__name__)

            # 首页
            @app.route('/', methods=['GET'])
            def index():
                return """
                <h1>Python网络自动化运维系统（简易版）</h1>
                <p>接口说明：</p>
                <ul>
                    <li>GET /inspect/[group_name] - 获取指定设备组巡检结果</li>
                    <li>示例：/inspect/switch_group_a</li>
                </ul>
                """

            # 巡检接口
            @app.route('/inspect/<group_name>', methods=['GET'])
            def get_inspect_result(group_name):
                try:
                    result = batch_inspect(group_name)
                    return jsonify({
                        "status": "success",
                        "group_name": group_name,
                        "inspect_result": result
                    })
                except Exception as e:
                    return jsonify({
                        "status": "error",
                        "message": str(e)
                    }), 500

            return app
        except ImportError:
            logger.warning("未安装Flask，Web服务不可用（执行 pip install flask 安装）")
            return None


    # 初始化备用Web服务
    flask_app = init_flask_app()


# ========== 系统菜单 ==========
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


# ========== 主程序逻辑 ==========
if __name__ == "__main__":
    logger.info("【系统启动】Python网络自动化运维系统开始运行")
    print("\n欢迎使用Python网络自动化运维系统！")

    while True:
        show_menu()
        choice = input("请输入操作编号：").strip()

        if choice == "1":
            # 1. 批量配置
            try:
                group_name = input("请输入设备组名：").strip()
                if not group_name:
                    print("错误：设备组名不能为空！")
                    continue
                tpl_name = input("请输入配置模板名（如vlan_tpl.txt）：").strip()
                if not tpl_name:
                    print("错误：配置模板名不能为空！")
                    continue
                tpl_kwargs_str = input("请输入模板参数（如{'vlan_id':10, 'vlan_name':'IT'}）：").strip()

                # 安全解析参数
                tpl_kwargs = ast.literal_eval(tpl_kwargs_str) if tpl_kwargs_str else {}

                logger.info(f"开始批量配置：设备组{group_name}，模板{tpl_name}，参数{tpl_kwargs}")
                result = batch_config(group_name, tpl_name, **tpl_kwargs)

                print("\n批量配置结果：")
                for k, v in result.items():
                    print(f"  {k}: {v}")
                logger.info(f"批量配置完成：{result}")
            except SyntaxError:
                logger.error("模板参数格式错误，请输入合法的JSON格式（如{'vlan_id':10}）")
                print("错误：模板参数格式错误，请输入合法的字典格式（如{'vlan_id':10, 'vlan_name':'IT'}）")
            except Exception as e:
                logger.error(f"批量配置失败：{str(e)}")
                print(f"配置失败：{str(e)}")

        elif choice == "2":
            # 2. 单次巡检
            try:
                group_name = input("请输入设备组名：").strip()
                if not group_name:
                    print("错误：设备组名不能为空！")
                    continue
                logger.info(f"开始单次巡检：设备组{group_name}")
                result = batch_inspect(group_name)

                # 兼容错误返回格式
                if "error" in result:
                    print(f"巡检失败：{result['error']}")
                else:
                    print("\n单次巡检结果汇总：")
                    for dev_name, dev_result in result.items():
                        print(f"  {dev_name}: {dev_result['status']}")
                        if dev_result['status'] == "巡检失败":
                            print(f"    原因：{dev_result['reason']}")
                logger.info(f"单次巡检完成：设备组{group_name}")
            except Exception as e:
                logger.error(f"单次巡检失败：{str(e)}")
                print(f"巡检失败：{str(e)}")

        elif choice == "3":
            # 3. 启动定时巡检
            try:
                interval = input("请输入巡检间隔（秒，默认3600）：").strip()
                interval = int(interval) if interval and interval.isdigit() else 3600
                if interval < 60:
                    print("警告：巡检间隔建议不小于60秒，已自动调整为60秒")
                    interval = 60

                group_names = input("请输入要巡检的设备组（逗号分隔，默认switch_group_a）：").strip()
                group_names = [g.strip() for g in group_names.split(",")] if group_names else ["switch_group_a"]
                # 过滤空值
                group_names = [g for g in group_names if g]

                # 启动子线程
                t = threading.Thread(
                    target=scheduled_inspect,
                    args=(interval, group_names),
                    daemon=True
                )
                t.start()

                logger.info(f"【定时巡检服务】已启动，间隔{interval}秒，巡检组：{group_names}")
                print(f"定时巡检服务已启动，日志查看运行状态（logs/main.log）")
            except ValueError:
                logger.error("巡检间隔输入错误：请输入数字")
                print("错误：巡检间隔必须是数字！")
            except Exception as e:
                logger.error(f"启动定时巡检失败：{str(e)}")
                print(f"启动失败：{str(e)}")

        elif choice == "4":
            # 4. 启动Web服务
            if not flask_app:
                print("Web服务启动失败：未安装Flask，请执行 pip install flask 安装")
                continue

            try:
                host = input("请输入Web服务监听地址（默认0.0.0.0）：").strip() or "0.0.0.0"
                port_input = input("请输入Web服务端口（默认5000）：").strip()
                port = int(port_input) if port_input and port_input.isdigit() else 5000

                # 启动子线程
                t = threading.Thread(
                    target=flask_app.run,
                    kwargs={"host": host, "port": port, "debug": False},
                    daemon=True
                )
                t.start()

                logger.info(f"【Web服务】已启动，访问地址：http://{host}:{port}")
                print(f"Web可视化服务已启动，访问地址：http://{host}:{port}")
            except ValueError:
                logger.error("Web端口输入错误：请输入数字")
                print("错误：端口号必须是数字！")
            except Exception as e:
                logger.error(f"启动Web服务失败：{str(e)}")
                print(f"启动失败：{str(e)}")

        elif choice == "0":
            # 0. 退出系统
            logger.info("【系统退出】Python网络自动化运维系统停止运行")
            print("系统退出，感谢使用！")
            sys.exit(0)

        else:
            print("输入错误，请重新输入有效的编号（0-4）！")
        print("\n" + "-" * 60 + "\n")