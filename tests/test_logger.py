#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logger import Logger

def main():
    """测试Logger类的功能"""
    print("开始测试Logger类...")
    
    # 创建测试配置
    config = {
        'level': 'DEBUG',
        'file_enabled': True,
        'file_path': 'data/logs/test_logger.log'
    }
    
    # 初始化Logger
    logger = Logger(config)
    
    # 获取命名日志记录器
    test_logger = logger.get_logger('test_module')
    
    # 测试不同级别的日志
    test_logger.debug("这是一条DEBUG级别的日志")
    test_logger.info("这是一条INFO级别的日志")
    test_logger.warning("这是一条WARNING级别的日志")
    test_logger.error("这是一条ERROR级别的日志")
    
    # 测试测试结果记录功能
    logger.log_test_result(
        user_type="正常用户",
        success=True,
        rba_triggered=False,
        details={
            "IP": "192.168.1.1",
            "设备": "Windows PC",
            "浏览器": "Chrome 100",
            "登录时间": "2025-04-09 10:30:00"
        }
    )
    
    logger.log_test_result(
        user_type="高风险用户",
        success=False,
        rba_triggered=True,
        details={
            "IP": "43.78.223.145 (外国)",
            "设备": "新设备",
            "浏览器": "异常UA",
            "登录时间": "2025-04-09 03:15:00",
            "触发项": "短信验证"
        }
    )
    
    print("Logger测试完成！")
    print(f"日志文件保存在: {os.path.abspath(config['file_path'])}")
    print("详细测试结果保存在 data/results/ 目录")

if __name__ == "__main__":
    main()