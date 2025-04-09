#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import json
from faker import Faker

class DeviceFingerprint:
    """设备指纹生成和管理工具，用于模拟不同设备特征"""
    
    def __init__(self):
        self.faker = Faker()
        # 预定义一些常用的分辨率
        self.common_resolutions = [
            {"width": 1366, "height": 768},  # 常见笔记本
            {"width": 1920, "height": 1080},  # 全高清显示器
            {"width": 2560, "height": 1440},  # QHD显示器
            {"width": 3840, "height": 2160},  # 4K显示器
            {"width": 375, "height": 812},    # iPhone X/XS/11 Pro
            {"width": 414, "height": 896},    # iPhone XR/11
            {"width": 360, "height": 740},    # 常见安卓手机
            {"width": 768, "height": 1024},   # iPad
        ]
        self.common_timezones = [
            "Asia/Shanghai",     # 中国
            "Asia/Tokyo",        # 日本
            "Asia/Singapore",    # 新加坡
            "Europe/London",     # 英国
            "Europe/Paris",      # 法国
            "America/New_York",  # 美国东部
            "America/Los_Angeles"  # 美国西部
        ]
        
    def generate_normal_user(self):
        """生成正常用户的设备指纹（固定的设备特征）"""
        fingerprint = {
            "viewport": self.common_resolutions[1],  # 1920x1080
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "timezone_id": "Asia/Shanghai",
            "locale": "zh-CN",
            "color_scheme": "no-preference",
            "reduced_motion": "no-preference",
            "has_touch": False,
            "is_mobile": False,
            "platform": "Windows",
            "cookies_enabled": True
        }
        return fingerprint
    
    def generate_high_risk_user(self):
        """生成高风险用户的设备指纹（不常见特征组合）"""
        # 随机选择一些不太常见的特性
        viewport = random.choice(self.common_resolutions[2:])  # 选择较不常见的分辨率
        timezone = random.choice(self.common_timezones[1:])  # 非中国时区
        
        # 随机选择模拟的平台
        platform = random.choice(["Linux", "Android", "iOS", "MacOS"])
        
        if platform == "Android" or platform == "iOS":
            is_mobile = True
            has_touch = True
            # 移动设备UA
            if platform == "Android":
                user_agent = "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36"
            else:
                user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
        else:
            is_mobile = False
            has_touch = random.choice([True, False])  # 电脑可能有触摸屏
            # 桌面设备UA
            if platform == "Linux":
                user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
            else:  # MacOS
                user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"
        
        fingerprint = {
            "viewport": viewport,
            "user_agent": user_agent,
            "timezone_id": timezone,
            "locale": random.choice(["en-US", "fr-FR", "de-DE", "ja-JP"]),
            "color_scheme": random.choice(["no-preference", "dark", "light"]),
            "reduced_motion": random.choice(["no-preference", "reduce"]),
            "has_touch": has_touch,
            "is_mobile": is_mobile,
            "platform": platform,
            "cookies_enabled": True
        }
        return fingerprint
    
    def generate_new_device_user(self):
        """生成新设备用户的指纹（有合理但与标准设备不同的特征）"""
        # 随机选择一个合理的分辨率
        viewport = random.choice(self.common_resolutions[:4])  # 桌面分辨率
        
        fingerprint = {
            "viewport": viewport,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",  # 较新版本
            "timezone_id": "Asia/Shanghai",  # 保持中国时区
            "locale": "zh-CN",
            "color_scheme": "no-preference",
            "reduced_motion": "no-preference",
            "has_touch": False,
            "is_mobile": False,
            "platform": "Windows",
            "cookies_enabled": True
        }
        return fingerprint
    
    def get_device_fingerprint(self, user_type="normal"):
        """
        获取指定用户类型的设备指纹
        
        Args:
            user_type: 用户类型，可选值为 "normal", "high_risk", "new_device"
            
        Returns:
            字典形式的设备指纹
        """
        if user_type == "high_risk":
            return self.generate_high_risk_user()
        elif user_type == "new_device":
            return self.generate_new_device_user()
        else:  # 默认为normal
            return self.generate_normal_user()
    
    def get_browser_args(self, user_type="normal"):
        """
        获取浏览器启动参数
        
        Args:
            user_type: 用户类型，可选值为 "normal", "high_risk", "new_device"
            
        Returns:
            浏览器启动参数字典
        """
        fingerprint = self.get_device_fingerprint(user_type)
        
        # 提取用户代理
        user_agent = fingerprint.get("user_agent", "")
        
        # 构造浏览器参数
        browser_args = []
        if user_agent:
            browser_args.append(f"--user-agent={user_agent}")
        
        return {
            "viewport": fingerprint.get("viewport"),
            "user_agent": user_agent,
            "timezone_id": fingerprint.get("timezone_id"),
            "locale": fingerprint.get("locale"),
            "color_scheme": fingerprint.get("color_scheme"),
            "reduced_motion": fingerprint.get("reduced_motion"),
            "args": browser_args
        }
    
    def create_browser_context_options(self, user_type="normal"):
        """
        创建浏览器上下文选项
        
        Args:
            user_type: 用户类型，可选值为 "normal", "high_risk", "new_device"
            
        Returns:
            用于创建浏览器上下文的选项字典
        """
        fingerprint = self.get_device_fingerprint(user_type)
        
        # 构建浏览器上下文选项
        context_options = {
            "viewport": fingerprint.get("viewport"),
            "user_agent": fingerprint.get("user_agent"),
            "timezone_id": fingerprint.get("timezone_id"),
            "locale": fingerprint.get("locale"),
            "color_scheme": fingerprint.get("color_scheme", "no-preference"),
            "reduced_motion": fingerprint.get("reduced_motion", "no-preference"),
            "has_touch": fingerprint.get("has_touch", False),
            "is_mobile": fingerprint.get("is_mobile", False),
        }
        
        return context_options
