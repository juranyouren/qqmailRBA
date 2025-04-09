#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
from playwright.sync_api import Page

class HumanBehavior:
    """模拟人类用户行为的工具类"""
    
    def __init__(self, config):
        """
        初始化人类行为模拟器
        
        Args:
            config: 行为配置参数，包含min_delay, max_delay, random_mouse, random_scroll
        """
        self.min_delay = config.get('min_delay', 0.5)
        self.max_delay = config.get('max_delay', 3.0)
        self.random_mouse = config.get('random_mouse', True)
        self.random_scroll = config.get('random_scroll', True)
    
    def random_delay(self, min_factor=1.0, max_factor=1.0):
        """
        模拟随机延迟，模拟人类操作间隔
        
        Args:
            min_factor: 最小延迟时间的倍率
            max_factor: 最大延迟时间的倍率
        """
        delay = random.uniform(
            self.min_delay * min_factor,
            self.max_delay * max_factor
        )
        time.sleep(delay)
    
    def human_like_typing(self, locator, text: str):
        """
        模拟人类输入行为
        
        Args:
            locator: Playwright的Locator对象（支持Page.locator或FrameLocator.locator）
            text: 要输入的文本
        """
        # 先聚焦元素
        locator.click()
        self.random_delay(0.2, 0.5)
        
        # 清除现有文本
        locator.fill("")
        self.random_delay(0.2, 0.5)
        
        # 逐个字符输入，模拟人类打字
        for char in text:
            locator.press(char, delay=random.uniform(100, 300))
            
            # 偶尔暂停一下，像人类思考
            if random.random() < 0.1:  # 10%的概率
                self.random_delay(0.5, 1.0)
    
    def human_like_click(self, page: Page, selector: str):
        """
        模拟人类点击行为，不总是点击元素中心
        
        Args:
            page: Playwright页面对象
            selector: 元素选择器
        """
        if not self.random_mouse:
            page.click(selector)
            return
        
        # 获取元素位置和尺寸
        element = page.query_selector(selector)
        if not element:
            raise ValueError(f"找不到元素: {selector}")
            
        bbox = element.bounding_box()
        
        # 随机选择元素内的点击位置，偏向中心区域
        x = bbox['x'] + bbox['width'] * (0.3 + random.random() * 0.4)
        y = bbox['y'] + bbox['height'] * (0.3 + random.random() * 0.4)
        
        # 移动鼠标到目标位置（可能带一些曲线轨迹）
        self._mouse_move_with_trajectory(page, x, y)
        
        # 点击
        page.mouse.click(x, y)
    
    def _mouse_move_with_trajectory(self, page: Page, target_x: float, target_y: float):
        """
        模拟鼠标移动轨迹，不是直线移动到目标
        
        Args:
            page: Playwright页面对象
            target_x: 目标X坐标
            target_y: 目标Y坐标
        """
        # 获取当前鼠标位置
        current_x, current_y = page.evaluate("""
            () => {
                return [window.mousePosX || 0, window.mousePosY || 0];
            }
        """)
        
        # 计算移动距离
        distance_x = target_x - current_x
        distance_y = target_y - current_y
        
        # 生成几个控制点，模拟自然鼠标轨迹
        steps = random.randint(3, 10)
        for i in range(steps):
            # 非线性轨迹
            progress = (i + 1) / steps
            easedProgress = progress * (2 - progress)  # 简单的easing函数
            
            # 添加一些随机性
            offset_x = random.gauss(0, distance_x * 0.05)
            offset_y = random.gauss(0, distance_y * 0.05)
            
            next_x = current_x + distance_x * easedProgress + offset_x
            next_y = current_y + distance_y * easedProgress + offset_y
            
            # 移动鼠标
            page.mouse.move(next_x, next_y)
            
            # 短暂延迟
            time.sleep(random.uniform(0.01, 0.1))
            
            # 更新JavaScript中的鼠标位置
            page.evaluate(f"""
                () => {{
                    window.mousePosX = {next_x};
                    window.mousePosY = {next_y};
                }}
            """)
    
    def scroll_randomly(self, page: Page):
        """
        模拟随机滚动页面行为
        
        Args:
            page: Playwright页面对象
        """
        if not self.random_scroll:
            return
            
        # 获取页面高度
        page_height = page.evaluate("""
            () => {
                return Math.max(
                    document.body.scrollHeight,
                    document.documentElement.scrollHeight
                );
            }
        """)
        
        # 随机滚动1-3次
        for _ in range(random.randint(1, 3)):
            # 随机滚动位置
            target_scroll = random.randint(100, max(200, page_height - 500))
            
            # 逐渐滚动，而不是一次性滚到目标位置
            current_pos = page.evaluate("() => window.scrollY")
            distance = target_scroll - current_pos
            
            steps = random.randint(3, 8)
            for i in range(steps):
                progress = (i + 1) / steps
                pos = current_pos + distance * progress
                
                page.evaluate(f"window.scrollTo(0, {pos})")
                time.sleep(random.uniform(0.05, 0.2))
            
            # 滚动后短暂停留，模拟阅读
            self.random_delay(0.5, 2.0)
