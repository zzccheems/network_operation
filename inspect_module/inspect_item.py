def inspect_interface(device_conn):
    """巡检：返回宕机接口列表"""
    cmd = "show ip interface brief" if "cisco" in device_conn.device_type else "display ip interface brief"
    output = device_conn.send_command(cmd)
    # 提取宕机接口
    down_interfaces = []
    for line in output.split("\n"):
        if "down" in line and "administratively down" not in line:
            intf = line.split()[0]
            down_interfaces.append(intf)
    return down_interfaces

def inspect_cpu(device_conn, warn_threshold=80):
    cmd = "show processes cpu | include CPU utilization" if "cisco" in device_conn.device_type else "display cpu-usage"
    output = device_conn.send_command(cmd)
    # 提取CPU使用率
    cpu_usage = int([x for x in output.split() if x.isdigit()][0])
    is_warn = cpu_usage >= warn_threshold
    return cpu_usage, is_warn

