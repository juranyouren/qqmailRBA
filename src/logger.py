#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from datetime import datetime

class Logger:
    """日志记录器，统一管理项目的日志记录"""
    
    def __init__(self, config):
        """
        初始化日志记录器
        
        Args:
            config: 日志配置，包含level, file_enabled, file_path
        """
        self.log_level_str = config.get('level', 'INFO')
        self.file_enabled = config.get('file_enabled', True)
        self.file_path = config.get('file_path', 'data/logs/rba_test.log')
        
        # 映射日志级别字符串到logging模块常量
        self.log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        self.log_level = self.log_levels.get(self.log_level_str.upper(), logging.INFO)
        
        # 设置日志记录器
        self.setup_logger()
    
    def setup_logger(self):
        """配置日志记录器"""
        # 获取根日志记录器
        logger = logging.getLogger()
        logger.setLevel(self.log_level)
        
        # 清除可能存在的处理器
        logger.handlers = []
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 添加文件处理器（如果启用）
        if self.file_enabled:
            # 确保日志目录存在
            log_dir = os.path.dirname(self.file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            try:
                file_handler = logging.FileHandler(self.file_path, encoding='utf-8')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                
                logging.info(f"日志将被保存到文件：{self.file_path}")
            except Exception as e:
                logging.error(f"无法创建日志文件处理器：{str(e)}")
        
        # 记录启动信息
        logging.info(f"日志系统初始化完成，级别：{self.log_level_str}")
    
    def get_logger(self, name):
        """
        获取命名的日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            命名的logger实例
        """
        return logging.getLogger(name)
    
    def log_test_result(self, user_type, success, rba_triggered, details):
        """
        记录测试结果
        
        Args:
            user_type: 用户类型
            success: 测试是否成功完成
            rba_triggered: 是否触发RBA机制
            details: 详细信息字典
        """
        logger = logging.getLogger('test_results')
        
        result_str = f"测试结果 [{user_type}] - "
        result_str += "成功" if success else "失败"
        result_str += " | RBA机制触发" if rba_triggered else " | 未触发RBA机制"
        
        if success:
            logger.info(result_str)
        else:
            logger.warning(result_str)
        
        # 记录详细信息
        for key, value in details.items():
            logger.info(f"  - {key}: {value}")
        
        # 如果启用了文件日志，将详细结果另存为JSON
        if self.file_enabled:
            import json
            from datetime import datetime
            
            result_data = {
                "timestamp": datetime.now().isoformat(),
                "user_type": user_type,
                "success": success,
                "rba_triggered": rba_triggered,
                "details": details
            }
            
            result_file = f"data/results/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_type}.json"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(result_file), exist_ok=True)
            
            try:
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                logger.info(f"详细测试结果已保存至：{result_file}")
            except Exception as e:
                logger.error(f"保存测试结果失败：{str(e)}")
