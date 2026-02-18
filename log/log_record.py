import logging
import os
from logging.handlers import TimedRotatingFileHandler
from config.config_read import SETTINGS

# 日志配置
LOG_SETTINGS = SETTINGS["log"]
LOG_PATH = LOG_SETTINGS["path"]
LOG_LEVEL = getattr(logging, LOG_SETTINGS["level"])

# 创建日志目录
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

# 定义日志格式
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
formatter = logging.Formatter(fmt)

# 初始化日志器
logger = logging.getLogger("net_automation")
logger.setLevel(LOG_LEVEL)
logger.handlers.clear()

# 1. 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 2. 文件日志处理器,保留7天
file_handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_PATH, "net_automation.log"),
    when="D",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 全局异常装饰器
def exception_catch(func):
    """装饰器：捕获函数异常，记录至日志"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"函数{func.__name__}执行异常：{str(e)}", exc_info=True)
            raise e
    return wrapper