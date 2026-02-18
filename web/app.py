from flask import Flask, render_template, jsonify
from config.config_read import SETTINGS, DEVICES
from batch_inspect import batch_inspect,logger
import os
import json

# 初始化Flask应用
app = Flask(__name__)
WEB_SETTINGS = SETTINGS["web"]

# 首页：设备状态总览
@app.route("/")
def index():
    # 读取所有设备组信息
    device_groups = list(DEVICES.keys())
    # 统计设备总数/在线数（简化版，实际从连接状态获取）
    total_device = sum([len(devices) for devices in DEVICES.values()])
    online_device = total_device - 0  # 实际需从连接结果统计
    return render_template("index.html",
                           device_groups=device_groups,
                           total_device=total_device,
                           online_device=online_device)

# API：获取设备组状态
@app.route("/api/device/group/<group_name>")
def get_device_group(group_name):
    if group_name not in DEVICES:
        return jsonify({"code": 404, "msg": "设备组不存在"})
    # 调用批量巡检，获取设备状态
    inspect_result = batch_inspect(group_name)
    return jsonify({"code": 200, "data": inspect_result})

# API：获取运维日志
@app.route("/api/log/<log_type>")
def get_log(log_type):
    # log_type: info/warning/error
    log_path = os.path.join(SETTINGS["log"]["path"], "net_automation.log")
    if not os.path.exists(log_path):
        return jsonify({"code": 404, "msg": "日志文件不存在"})
    # 读取日志并过滤指定类型
    logs = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f.readlines()[-1000:]:  # 仅读取最后1000行，提升性能
            if log_type.upper() in line:
                logs.append(line.strip())
    return jsonify({"code": 200, "data": logs[::-1]})  # 倒序展示，最新的在前

# 巡检报告页面
@app.route("/inspect")
def inspect():
    # 读取所有巡检报告
    report_path = "./inspect_report/"
    if not os.path.exists(report_path):
        os.makedirs(report_path)
    report_files = [f for f in os.listdir(report_path) if f.endswith(".json")]
    report_files.sort(reverse=True)  # 按时间倒序
    return render_template("inspect.html", report_files=report_files)

# 启动Web服务
if __name__ == "__main__":
    app.run(host=WEB_SETTINGS["host"], port=WEB_SETTINGS["port"], debug=False)