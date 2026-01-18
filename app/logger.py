import logging
import logging.handlers
import os
from datetime import datetime


def setup_logger():
    """
    配置应用日志
    
    特性:
    - 控制台输出（INFO级别及以上）
    - 文件输出（DEBUG级别及以上）
    - 按日期轮转日志文件
    - 统一的日志格式
    
    Returns:
        logging.Logger: 配置好的logger实例
    """
    
    # 创建logs目录如果不存在
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger('are_you_ok')
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器 (INFO级别)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 所有日志 (DEBUG级别)
    log_file = os.path.join(logs_dir, 'app.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,  # 保留10个备份文件
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 错误日志处理器 (ERROR级别)
    error_log_file = os.path.join(logs_dir, 'error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # 保留5个备份文件
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


def get_logger():
    """
    获取logger实例
    
    Returns:
        logging.Logger: logger实例
    """
    return logging.getLogger('are_you_ok')
