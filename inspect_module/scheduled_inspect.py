import schedule
import time
from batch_inspect import batch_inspect,logger,INSPECT_SETTINGS

def scheduled_inspect():
    """定时巡检任务：巡检所有设备组"""
    logger.info("【定时巡检】开始执行全设备组巡检")
    from config.config_read import DEVICES
    for group_name in DEVICES.keys():
        batch_inspect(group_name)
    logger.info("【定时巡检】全设备组巡检执行完成")

# 启动定时任务
if __name__ == "__main__":
    # 按配置的间隔执行
    schedule.every(INSPECT_SETTINGS["interval"]).seconds.do(scheduled_inspect)
    scheduled_inspect()
    # 保持任务运行
    while True:
        schedule.run_pending()
        time.sleep(1)