import sys
from loguru import logger

def setup_logger():
    """配置 loguru 日志格式。"""
    logger.remove()
    
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    logger.add(sys.stdout, format=log_format, level="INFO")
    return logger

# 初始化
logger = setup_logger()
