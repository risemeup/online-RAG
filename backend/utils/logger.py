import configparser
import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(log_level=logging.INFO, name="root"):
    logger = logging.getLogger(name)

    # Avoid printing multiple logs
    logger.propagate = False

    root_dir = get_log_root_dir()
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if not logger.handlers:
        log_handler = RotatingFileHandler(
            os.path.join(root_dir, name + ".log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        logger.setLevel(log_level)
        log_format = logging.Formatter(
            "[%(asctime)-15s] [%(levelname)8s] %(filename)s:%(lineno)s - %(message)s"
        )
        log_handler.setFormatter(log_format)
        logger.addHandler(log_handler)
    else:
        logger.setLevel(log_level)
    return logger


def get_log_root_dir():
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../config/common.ini"
    )
    
    # 如果配置文件存在，尝试读取配置
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8")
        if "log" in config and "root_dir" in config["log"]:
            return config["log"]["root_dir"]
    
    # 如果配置文件不存在或没有log配置，使用默认的logs目录
    default_log_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../logs"
    )
    return os.path.abspath(default_log_dir)
