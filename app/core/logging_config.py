"""统一日志配置"""
import logging
import sys
from typing import Optional

def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    apscheduler_level: str = "INFO"  # 单独控制 APScheduler 日志级别
):
    """
    统一配置应用日志
    
    Args:
        level: 应用日志级别
        format_string: 日志格式
        apscheduler_level: APScheduler 日志级别
    """
    
    # 默认日志格式
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # 强制重新配置，覆盖之前的配置
    )
    
    # 配置 APScheduler 日志
    apscheduler_logger = logging.getLogger('apscheduler')
    apscheduler_logger.setLevel(getattr(logging, apscheduler_level.upper()))
    
    # 如果你想看到定时任务执行日志，设置为 INFO
    # 如果你想减少日志噪音，设置为 WARNING
    logging.getLogger('apscheduler.executors.default').setLevel(getattr(logging, apscheduler_level.upper()))
    logging.getLogger('apscheduler.scheduler').setLevel(getattr(logging, apscheduler_level.upper()))
    logging.getLogger('apscheduler.jobstores.default').setLevel(getattr(logging, apscheduler_level.upper()))
    
    # 配置其他第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # 获取应用 logger
    app_logger = logging.getLogger(__name__)
    app_logger.info("📝 日志系统配置完成")
    
    return app_logger

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的 logger"""
    return logging.getLogger(name)
