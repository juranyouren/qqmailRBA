#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import logging
import json
import os
from datetime import datetime

class ProxyManager:
    """代理IP管理器，用于管理和选择测试使用的代理服务器"""
    
    def __init__(self, proxy_config):
        """
        初始化代理管理器
        
        Args:
            proxy_config: 代理配置字典，包含enabled, servers, random等
        """
        self.enabled = proxy_config.get('enabled', False)
        self.servers = proxy_config.get('servers', [])
        self.use_random = proxy_config.get('random', True)
        
        # 初始化日志
        self.logger = logging.getLogger('proxy_manager')
        
        # 确保至少有一个服务器
        if self.enabled and not self.servers:
            self.logger.warning("代理功能已启用但未配置服务器，将禁用代理")
            self.enabled = False
        
        # 代理使用记录
        self.usage_history = []
        
        # 加载历史记录
        self._load_history()
    
    def _load_history(self):
        """加载代理使用历史记录"""
        history_path = "data/proxy_history.json"
        
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    self.usage_history = json.load(f)
                self.logger.debug(f"加载了 {len(self.usage_history)} 条代理使用记录")
            except Exception as e:
                self.logger.error(f"加载代理历史记录失败: {str(e)}")
    
    def _save_history(self):
        """保存代理使用历史记录"""
        history_path = "data/proxy_history.json"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        
        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.usage_history, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"保存了 {len(self.usage_history)} 条代理使用记录")
        except Exception as e:
            self.logger.error(f"保存代理历史记录失败: {str(e)}")
    
    def get_proxy(self, user_type="normal"):
        """
        根据用户类型获取适合的代理服务器
        
        Args:
            user_type: 用户类型，可选值为 "normal", "high_risk", "new_device"
            
        Returns:
            代理服务器URL字符串，如果禁用代理则返回None
        """
        if not self.enabled or not self.servers:
            return None
        
        if user_type == "normal":
            # 正常用户使用固定代理
            proxy_server = self.servers[0] if self.servers else None
        elif user_type == "high_risk":
            # 高风险用户每次使用不同代理
            proxy_server = random.choice(self.servers) if self.use_random else self.servers[-1]
        else:  # new_device
            # 新设备用户使用不同于常用代理的服务器
            if len(self.servers) > 1:
                proxy_server = self.servers[1]
            else:
                proxy_server = self.servers[0]
        
        # 记录代理使用情况
        self._record_proxy_usage(proxy_server, user_type)
        
        return proxy_server
    
    def _record_proxy_usage(self, proxy_server, user_type):
        """记录代理使用情况"""
        if not proxy_server:
            return
            
        record = {
            "timestamp": datetime.now().isoformat(),
            "proxy": proxy_server,
            "user_type": user_type
        }
        
        self.usage_history.append(record)
        
        # 如果历史记录过长，只保留最近的1000条
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]
        
        # 保存历史
        self._save_history()
    
    def get_playwright_proxy_config(self, user_type="normal"):
        """
        获取Playwright格式的代理配置
        
        Args:
            user_type: 用户类型
            
        Returns:
            适用于Playwright的代理配置字典或None
        """
        proxy_server = self.get_proxy(user_type)
        
        if not proxy_server:
            return None
            
        return {"server": proxy_server}
