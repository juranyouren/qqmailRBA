#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import logging

class ConfigLoader:
    """配置文件加载器，用于读取和处理配置文件"""
    
    def __init__(self, config_path='config/config.ini'):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger('config_loader')
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        
        # 尝试加载配置
        self.load_config()
        
    def load_config(self):
        """加载配置文件，如果不存在则使用示例配置"""
        # 检查配置文件是否存在
        if not os.path.exists(self.config_path):
            self.logger.warning(f"配置文件 {self.config_path} 不存在，尝试使用示例配置")
            # 尝试加载示例配置
            example_config_path = 'config/config.example.ini'
            if not os.path.exists(example_config_path):
                raise FileNotFoundError(f"配置文件和示例配置文件都不存在: {self.config_path}, {example_config_path}")
            
            self.config_path = example_config_path
        
        # 加载配置
        self.config.read(self.config_path, encoding='utf-8')
        self.logger.info(f"已成功加载配置文件: {self.config_path}")
    
    def get_credentials(self):
        """获取登录凭证配置"""
        if not self.config.has_section('credentials'):
            self.logger.error("配置文件中缺少 'credentials' 部分")
            return {"email": "", "password": ""}
        
        email = self.config.get('credentials', 'email', fallback='')
        password = self.config.get('credentials', 'password', fallback='')
        
        if not email or not password or email == 'your_test_email@qq.com':
            self.logger.warning("未正确配置测试账号信息，请编辑config.ini文件")
        
        return {
            "email": email,
            "password": password
        }
    
    def get_proxy_config(self):
        """获取代理配置"""
        if not self.config.has_section('proxy'):
            return {"enabled": False, "servers": [], "random": True}
        
        enabled = self.config.getboolean('proxy', 'enabled', fallback=False)
        servers_str = self.config.get('proxy', 'servers', fallback='')
        random_proxy = self.config.getboolean('proxy', 'random', fallback=True)
        
        # 解析代理服务器列表
        servers = [s.strip() for s in servers_str.split(',') if s.strip()]
        
        return {
            "enabled": enabled,
            "servers": servers,
            "random": random_proxy
        }
    
    def get_user_agents(self):
        """获取User-Agent配置"""
        result = {}
        
        if self.config.has_section('user_agents'):
            for key, value in self.config.items('user_agents'):
                result[key] = value
        
        return result
    
    def get_test_scenarios(self):
        """获取测试场景配置"""
        if not self.config.has_section('test_scenarios'):
            return {"normal_user": True, "high_risk_user": True, "new_device_user": True}
        
        return {
            "normal_user": self.config.getboolean('test_scenarios', 'normal_user', fallback=True),
            "high_risk_user": self.config.getboolean('test_scenarios', 'high_risk_user', fallback=True),
            "new_device_user": self.config.getboolean('test_scenarios', 'new_device_user', fallback=True)
        }
    
    def get_behavior_config(self):
        """获取人类行为模拟配置"""
        if not self.config.has_section('behavior'):
            return {
                "min_delay": 0.5,
                "max_delay": 3.0,
                "random_mouse": True,
                "random_scroll": True
            }
        
        return {
            "min_delay": self.config.getfloat('behavior', 'min_delay', fallback=0.5),
            "max_delay": self.config.getfloat('behavior', 'max_delay', fallback=3.0),
            "random_mouse": self.config.getboolean('behavior', 'random_mouse', fallback=True),
            "random_scroll": self.config.getboolean('behavior', 'random_scroll', fallback=True)
        }
    
    def get_logging_config(self):
        """获取日志配置"""
        if not self.config.has_section('logging'):
            return {
                "level": "INFO",
                "file_enabled": True,
                "file_path": "data/logs/rba_test.log"
            }
        
        return {
            "level": self.config.get('logging', 'level', fallback='INFO'),
            "file_enabled": self.config.getboolean('logging', 'file_enabled', fallback=True),
            "file_path": self.config.get('logging', 'file_path', fallback='data/logs/rba_test.log')
        }
