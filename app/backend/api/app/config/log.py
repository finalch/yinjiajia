import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 日志配置
LOG_PATH = 'logs/ecommerce.log'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'NOTSET').upper()
LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    """设置指定模块的logger"""
    logger = logging.getLogger(name)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    # 文件处理器 - 按大小轮转
    file_handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.NOTSET)
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """获取logger实例"""
    return setup_logger(name) 