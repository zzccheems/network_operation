#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络自动化运维系统 - Web 可视化模块
路径：network_operation/web/app.py
"""
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, redirect, url_for
# 导入核心功能模块
from inspect_module.batch_inspect import batch_inspect
from configure.batch_configuration import batch_config
from log.log_record import logger  # 如果有独立日志模块，否则用内置

# 初始化Flask应用
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))

# ========== 全局配置 ==========
# 巡检报告目录
INSPECT_REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  "inspect_module", "inspect_report")
# 配置模板目录
CONFIG_TPL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                              "configure", "templates")
# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

# 确保目录存在
for dir_path in [INSPECT_REPORT_DIR, CONFIG_TPL_DIR, LOG_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# ========== 页面路由 ==========
@app.route('/')
def index():
    """首页：系统概览"""
    # 获取所有设备组（从devices.yaml读取）
    try:
        from config.config_read import DEVICES
        group_names = list(DEVICES.keys()) if isinstance(DEVICES, dict) else []
    except:
        group_names = ["switch_group_a", "router_group_b"]

    return render_template('index.html',
                           group_names=group_names,
                           current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@app.route('/inspect', methods=['GET', 'POST'])
def inspect_page():
    """设备巡检页面"""
    if request.method == 'POST':
        # 执行巡检
        group_name = request.form.get('group_name')
        if not group_name:
            return jsonify({"status": "error", "message": "请选择设备组"})

        try:
            # 执行批量巡检
            result = batch_inspect(group_name)
            # 保存巡检结果（和本地报告同步）
            report_name = f"{group_name}_inspect_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            report_path = os.path.join(INSPECT_REPORT_DIR, report_name)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            logger.info(f"Web端执行巡检：{group_name}，结果已保存至 {report_name}")
            return jsonify({
                "status": "success",
                "group_name": group_name,
                "result": result,
                "report_name": report_name
            })
        except Exception as e:
            logger.error(f"Web端巡检失败：{str(e)}")
            return jsonify({"status": "error", "message": str(e)})

    # GET请求：展示巡检页面
    try:
        from config.config_read import DEVICES
        group_names = list(DEVICES.keys()) if isinstance(DEVICES, dict) else []
    except:
        group_names = ["switch_group_a", "router_group_b"]

    # 获取历史巡检报告
    report_files = []
    if os.path.exists(INSPECT_REPORT_DIR):
        report_files = [f for f in os.listdir(INSPECT_REPORT_DIR) if f.endswith('.json')]
        report_files.sort(reverse=True)  # 按时间倒序

    return render_template('inspect.html',
                           group_names=group_names,
                           report_files=report_files[:10])  # 只显示最近10个报告


@app.route('/config', methods=['GET', 'POST'])
def config_page():
    """批量配置页面"""
    if request.method == 'POST':
        # 执行批量配置
        group_name = request.form.get('group_name')
        tpl_name = request.form.get('tpl_name')
        tpl_params = request.form.get('tpl_params')

        if not group_name or not tpl_name:
            return jsonify({"status": "error", "message": "设备组和模板名不能为空"})

        try:
            # 解析模板参数
            import ast
            tpl_kwargs = ast.literal_eval(tpl_params) if tpl_params else {}
            # 执行批量配置
            result = batch_config(group_name, tpl_name, **tpl_kwargs)

            logger.info(f"Web端执行配置：{group_name}，模板{tpl_name}，参数{tpl_kwargs}")
            return jsonify({
                "status": "success",
                "group_name": group_name,
                "result": result
            })
        except Exception as e:
            logger.error(f"Web端配置失败：{str(e)}")
            return jsonify({"status": "error", "message": str(e)})

    # GET请求：展示配置页面
    try:
        from config.config_read import DEVICES
        group_names = list(DEVICES.keys()) if isinstance(DEVICES, dict) else []
    except:
        group_names = ["switch_group_a", "router_group_b"]

    # 获取配置模板列表
    tpl_files = []
    if os.path.exists(CONFIG_TPL_DIR):
        tpl_files = [f for f in os.listdir(CONFIG_TPL_DIR) if f.endswith(('.txt', '.tpl'))]

    return render_template('config.html',
                           group_names=group_names,
                           tpl_files=tpl_files)


@app.route('/logs')
def logs_page():
    """日志查看页面"""
    log_files = []
    if os.path.exists(LOG_DIR):
        log_files = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]

    # 默认显示main.log
    log_content = ""
    selected_log = request.args.get('log_file', 'main.log')
    log_path = os.path.join(LOG_DIR, selected_log)

    if os.path.exists(log_path):
        # 读取最后100行，避免日志过大
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            log_content = ''.join(lines[-100:])  # 只显示最后100行

    return render_template('logs.html',
                           log_files=log_files,
                           selected_log=selected_log,
                           log_content=log_content)


@app.route('/report/<report_name>')
def view_report(report_name):
    """查看历史巡检报告"""
    report_path = os.path.join(INSPECT_REPORT_DIR, report_name)
    if not os.path.exists(report_path):
        return jsonify({"status": "error", "message": "报告文件不存在"})

    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    return render_template('report_view.html',
                           report_name=report_name,
                           report_data=report_data)


# ========== 错误处理 ==========
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', error_msg=str(e)), 500


# ========== 启动入口 ==========
if __name__ == '__main__':
    # 开发环境启动（生产环境建议用Gunicorn）
    app.run(host='0.0.0.0', port=5000, debug=False)