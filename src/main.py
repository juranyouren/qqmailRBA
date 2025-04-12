#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
import time

from config_loader import ConfigLoader
from logger import Logger
from proxy_manager import ProxyManager
from device_fingerprint import DeviceFingerprint
from human_behavior import HumanBehavior

def setup_environment():
    """设置环境，创建必要的目录"""
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/results", exist_ok=True)

def validate_page_structure(page, dynamic_selectors):
    """验证页面结构是否符合预期"""
    logger = logging.getLogger('page_validator')
    logger.info("开始验证页面结构")

    for selector in dynamic_selectors:
        try:
            count = page.locator(selector).count()
            logger.info(f"选择器 {selector}: 找到 {count} 个元素")
            if count > 0:
                try:
                    text = page.locator(selector).first.inner_text()
                    logger.info(f"第一个 {selector} 元素的文本: {text}")
                except Exception as e:
                    logger.warning(f"无法获取选择器 {selector} 的文本: {str(e)}")
        except Exception as e:
            logger.warning(f"检查选择器 {selector} 时出错: {str(e)}")

def perform_login_test(browser_type, config, user_type="normal"):
    """执行登录测试
    
    Args:
        browser_type: Playwright浏览器类型
        config: 配置对象
        user_type: 用户类型，可选值为 "normal", "high_risk", "new_device"
    """
    logger = logging.getLogger('login_test')
    logger.info(f"开始执行 {user_type} 类型用户的登录测试")
    
    # 获取登录凭证
    credentials = config.get_credentials()
    if not credentials.get('email') or not credentials.get('password'):
        logger.error("没有配置测试账号，无法进行测试")
        return
    
    # 准备设备指纹
    device = DeviceFingerprint()
    context_options = device.create_browser_context_options(user_type)
    logger.info(f"使用设备指纹: {user_type}")
    
    # 准备代理
    proxy_manager = ProxyManager(config.get_proxy_config())
    proxy = proxy_manager.get_playwright_proxy_config(user_type)
    if proxy:
        context_options['proxy'] = proxy
        logger.info(f"使用代理: {proxy['server']}")
    
    # 创建浏览器上下文
    browser = browser_type.launch(headless=False)
    context = browser.new_context(**context_options)
    page = context.new_page()
    
    # 设置人类行为模拟器
    behavior = HumanBehavior(config.get_behavior_config())
    
    try:
        # 访问QQ邮箱登录页面
        logger.info("访问QQ邮箱登录页面")
        page.goto("https://mail.qq.com/", timeout=60000)  # 增加超时时间到60秒
        logger.info("页面加载完成，等待页面稳定")
        
        # 增加页面稳定等待时间
        page.wait_for_load_state('networkidle')
        behavior.random_delay(5.0, 8.0)  # 增加延迟时间，确保页面完全加载
        
        # 验证页面结构
        dynamic_selectors = config.get_dynamic_selectors()
        validate_page_structure(page, dynamic_selectors)
        
        # 查看页面上所有可能的登录按钮并记录
        logger.info("分析页面登录元素")
        page.screenshot(path=f"data/screenshots/login_page_initial_{user_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        # 打印页面文本内容以帮助分析
        logger.info(f"页面标题: {page.title()}")
        logger.info(f"页面文本: {page.inner_text('body')[:200]}...")  # 只打印前200个字符避免日志过长
        
        # 查找所有iframe以便分析
        iframe_count = page.locator('iframe').count()
        logger.info(f"页面中找到 {iframe_count} 个iframe")
        for i in range(iframe_count):
            try:
                iframe_src = page.locator('iframe').nth(i).get_attribute('src') or ""
                iframe_id = page.locator('iframe').nth(i).get_attribute('id') or ""
                iframe_name = page.locator('iframe').nth(i).get_attribute('name') or ""
                logger.info(f"iframe {i}: id='{iframe_id}', name='{iframe_name}', src='{iframe_src}'")
            except Exception as e:
                logger.warning(f"获取iframe {i}信息时出错: {str(e)}")
        
        # 尝试查找各种可能的登录元素
        potential_selectors = [
            'a#switcher_plogin',  # 原来使用的选择器
            '#switcher_plogin',   # 不带a标签的选择器
            '.login_login_btn',   # 可能的登录按钮类名
            'a:has-text("密码登录")',  # 包含"密码登录"文本的a标签
            'button:has-text("密码登录")', # 包含"密码登录"文本的按钮
            'a:has-text("QQ登录")',   # 包含"QQ登录"文本的a标签
            '.login-switch-item:has-text("QQ登录")',  # 可能的QQ登录元素
            'a.login',  # 可能的新登录按钮
            'button.login',  # 可能的新登录按钮
            '.btlogin',  # 可能的新登录按钮类
            '.login_btn',  # 可能的新登录按钮类
            '[title="登录"]',  # 带有登录标题的元素
            'a[href*="xlogin"]',  # 可能链接到登录页面的元素
            'a:has-text("登录")',  # 包含"登录"文本的a标签
            'button:has-text("登录")', # 包含"登录"文本的按钮
            'iframe[src*="xlogin"]' # 可能的登录iframe
        ]
        
        for selector in potential_selectors:
            try:
                count = page.locator(selector).count()
                logger.info(f"选择器 {selector}: 找到 {count} 个元素")
                if count > 0:
                    try:
                        text = page.locator(selector).first.inner_text()
                        logger.info(f"第一个 {selector} 元素的文本: {text}")
                    except:
                        logger.info(f"第一个 {selector} 元素无法获取文本")
            except Exception as e:
                logger.warning(f"检查选择器 {selector} 时出错: {str(e)}")
        
        # 检查登录界面是否有切换到QQ登录的标签
        logger.info("检查登录方式切换标签")
        try:
            # 检查是否存在QQ登录标签并点击
            if page.locator("#QQMailSdkTool_login_loginBox_tab_item_qq").is_visible():
                logger.info("找到QQ登录标签，确保选中QQ登录方式")
                page.locator("#QQMailSdkTool_login_loginBox_tab_item_qq").click()
                logger.info("已点击QQ登录标签")
                behavior.random_delay(1.0, 2.0)
            else:
                logger.info("未找到QQ登录标签，尝试其他方式")
        except Exception as e:
            logger.warning(f"切换QQ登录标签时出错: {str(e)}")
            # 继续执行，因为可能已经默认为QQ登录
        
        # 首先点击页面上的"密码登录"按钮
        logger.info("尝试点击页面上的密码登录按钮")
        try:
            # 尝试使用JavaScript方式查找和点击密码登录按钮
            logger.info("尝试使用JavaScript查找和点击密码登录按钮")
            try:
                # 尝试在主页面查找密码登录按钮
                has_button = page.evaluate("""
                    () => {
                        const btn = document.getElementById("switcher_plogin");
                        if (btn) {
                            console.log("在主页面找到密码登录按钮");
                            return true;
                        }
                        return false;
                    }
                """)
                
                if has_button:
                    logger.info("在主页面找到密码登录按钮，尝试点击")
                    page.evaluate("document.getElementById('switcher_plogin').click()")
                    logger.info("已通过JavaScript点击密码登录按钮")
                    behavior.random_delay(1.0, 2.0)
                else:
                    logger.info("在主页面未找到密码登录按钮，尝试在iframe中查找")
                    
                    # 尝试在登录iframe中查找
                    login_frame = page.frame('iframe#login_frame')
                    if login_frame:
                        has_button_in_frame = login_frame.evaluate("""
                            () => {
                                const btn = document.getElementById("switcher_plogin");
                                if (btn) {
                                    console.log("在iframe中找到密码登录按钮");
                                    btn.click();
                                    return true;
                                }
                                return false;
                            }
                        """)
                        
                        if has_button_in_frame:
                            logger.info("已通过JavaScript在iframe中点击密码登录按钮")
                            behavior.random_delay(1.0, 2.0)
                        else:
                            logger.warning("在iframe中未找到密码登录按钮")
                    else:
                        logger.warning("未找到登录iframe")
            except Exception as js_error:
                logger.warning(f"使用JavaScript查找密码登录按钮时出错: {str(js_error)}")
            
            # 如果JavaScript方法失败，回退到原始方法
            # 修改 iframe 处理部分的代码
            login_frame = page.frame('iframe#login_frame')  # 获取 Frame 对象
            if login_frame:
                login_frame.locator('a#switcher_plogin').wait_for(state='visible', timeout=15000)
                login_frame.locator('a#switcher_plogin').click()  # 添加 'a' 标签选择器
                behavior.random_delay(1.0, 2.0)  # 点击后稍等片刻
        except Exception as e:
            logger.warning(f"无法找到或点击页面上的密码登录按钮: {str(e)}")
            # 继续尝试查找登录框，因为有些情况下可能不需要点击此按钮
        
        # 处理可能的登录框iframe
        logger.info("处理登录框")
        
        # 等待登录框iframe出现（最长30秒）
        try:
            logger.info("等待iframe加载...")
            page.wait_for_selector('iframe#login_frame', timeout=30000)
            logger.info("iframe已加载")
            
            # 获取登录框
            login_frame = page.frame_locator('iframe#login_frame')
            
            # 截图便于调试
            page.screenshot(path=f"data/screenshots/login_page_{user_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            # 先点击"密码登录"按钮
            logger.info("点击密码登录按钮")
            # 等待密码登录按钮可点击
            login_frame.locator('#switcher_plogin').wait_for(state='visible', timeout=10000)
            login_frame.locator('#switcher_plogin').click()
            behavior.random_delay(1.0, 2.0)  # 点击后稍等片刻
            
            # 等待用户名输入框可用
            login_frame.locator('#u').wait_for(state='visible', timeout=5000)
            
            # 输入用户名
            logger.info("输入用户名")
            behavior.human_like_typing(
                login_frame.locator('#u'), 
                credentials['email'].split('@')[0]  # QQ邮箱通常只需要输入@前面的部分
            )
            behavior.random_delay()
            
            # 输入密码
            logger.info("输入密码")
            behavior.human_like_typing(
                login_frame.locator('#p'), 
                credentials['password']
            )
            behavior.random_delay()
            
            # 点击登录按钮
            logger.info("点击登录按钮")
            login_frame.locator('#login_button').click()
            
            # 等待页面加载
            page.wait_for_load_state('networkidle')
            behavior.random_delay(2.0, 5.0)
            
            # 检测是否有安全验证
            if "QQ安全中心" in page.title() or page.locator('text=安全验证').count() > 0:
                logger.warning("检测到安全验证，RBA机制已触发")
                return {
                    "success": False,
                    "rba_triggered": True,
                    "details": {
                        "用户类型": user_type,
                        "页面标题": page.title(),
                        "登录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "触发项": "安全验证"
                    }
                }
            else:
                logger.info("登录成功，未触发RBA机制")
                return {
                    "success": True,
                    "rba_triggered": False,
                    "details": {
                        "用户类型": user_type,
                        "页面标题": page.title(),
                        "登录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
        
        except Exception as e:
            logger.warning(f"处理标准登录框时出错: {str(e)}")
            
            # 尝试其他可能的选择器
            alternative_selectors = ['iframe[name="login_frame"]', 'iframe[src*="xlogin"]']
            for selector in alternative_selectors:
                logger.info(f"尝试使用备选选择器: {selector}")
                if page.locator(selector).count() > 0:
                    logger.info(f"找到登录框使用选择器: {selector}")
                    login_frame = page.frame_locator(selector)
                    
                    # 先点击"密码登录"按钮
                    logger.info("尝试点击密码登录按钮")
                    try:
                        login_frame.locator('#switcher_plogin').wait_for(state='visible', timeout=5000)
                        login_frame.locator('#switcher_plogin').click()
                        behavior.random_delay(1.0, 2.0)  # 点击后稍等片刻
                        
                        # 等待用户名输入框可用
                        login_frame.locator('#u').wait_for(state='visible', timeout=5000)
                        
                        # 输入用户名和密码并登录
                        behavior.human_like_typing(
                            login_frame.locator('#u'), 
                            credentials['email'].split('@')[0]
                        )
                        behavior.random_delay()
                        
                        behavior.human_like_typing(
                            login_frame.locator('#p'), 
                            credentials['password']
                        )
                        behavior.random_delay()
                        
                        login_frame.locator('#login_button').click()
                        
                        # 等待页面加载
                        page.wait_for_load_state('networkidle')
                        behavior.random_delay(2.0, 5.0)
                        
                        # 检测是否有安全验证
                        if "QQ安全中心" in page.title() or page.locator('text=安全验证').count() > 0:
                            logger.warning("检测到安全验证，RBA机制已触发")
                            return {
                                "success": False,
                                "rba_triggered": True,
                                "details": {
                                    "用户类型": user_type,
                                    "页面标题": page.title(),
                                    "登录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "触发项": "安全验证"
                                }
                            }
                        else:
                            logger.info("登录成功，未触发RBA机制")
                            return {
                                "success": True,
                                "rba_triggered": False,
                                "details": {
                                    "用户类型": user_type,
                                    "页面标题": page.title(),
                                    "登录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            }
                    except Exception as e:
                        logger.warning(f"使用备选选择器 {selector} 时出错: {str(e)}")
                        continue
            
            # 遍历所有 iframe，尝试找到目标元素
            logger.info("开始遍历所有 iframe，查找密码登录按钮")
            all_iframes = page.frames
            for iframe in all_iframes:
                try:
                    logger.info(f"检查 iframe: {iframe.url}")
                    if iframe.url and "oauth2.0/authorize" in iframe.url:
                        logger.info("找到目标 iframe，尝试查找密码登录按钮")

                        # 切换到密码登录方式
                        password_login_button = iframe.locator('a#switcher_plogin')
                        if password_login_button.count() > 0:
                            password_login_button.click()
                            logger.info("成功点击密码登录按钮")
                            behavior.random_delay(1.0, 2.0)
                            break
                        else:
                            logger.warning("目标 iframe 中未找到密码登录按钮")
                except Exception as e:
                    logger.warning(f"处理 iframe 时出错: {str(e)}")

            else:
                logger.error("未能在任何 iframe 中找到密码登录按钮")
                page.screenshot(path='data/screenshots/failed_to_find_password_login.png')
            
            # 如果尝试查找标准iframe失败，尝试oauth认证iframe
            try:
                logger.info("处理QQ OAuth iframe...")
                page.wait_for_selector('iframe[src*="oauth2.0/authorize"]', timeout=40000)
                oauth_frame = page.frame_locator('iframe[src*="oauth2.0/authorize"]')

                # 切换到密码登录
                oauth_frame.locator('a:has-text("帐号密码登录")').wait_for(state='visible', timeout=20000)
                oauth_frame.locator('a:has-text("帐号密码登录")').click()
                behavior.random_delay(1.0, 2.0)

                # 输入账号
                oauth_frame.locator('input#u').fill(credentials['email'].split('@')[0])
                behavior.random_delay(0.5, 1.0)

                # 输入密码
                oauth_frame.locator('input#p').fill(credentials['password'])
                behavior.random_delay(0.5, 1.0)

                # 点击登录
                oauth_frame.locator('button#login_button').click()
                page.wait_for_load_state('networkidle')

                # 检查安全验证
                if page.locator('text=安全验证').count() > 0:
                    logger.warning("RBA机制触发：需要安全验证")
                    return {"success": False, "rba_triggered": True}
                else:
                    logger.info("登录成功")
                    return {"success": True, "rba_triggered": False}

            except Exception as e:
                logger.error(f"OAuth登录失败: {str(e)}")
                page.screenshot(path='data/screenshots/oauth_error.png')
                return {"success": False, "rba_triggered": False}
            
            # 如果尝试查找标准iframe失败，尝试直接在页面上查找登录表单
            logger.info("尝试直接在页面上查找登录表单")
            
            # 可能的用户名输入框选择器
            username_selectors = ['#u', 'input[name="account"]', 'input[type="text"][name="uin"]', 
                                'input[placeholder*="帐号"]', 'input[placeholder*="账号"]', 'input[placeholder*="QQ"]']
            
            # 可能的密码输入框选择器
            password_selectors = ['#p', 'input[type="password"]', 'input[name="password"]', 
                                'input[placeholder*="密码"]']
            
            # 可能的登录按钮选择器
            login_button_selectors = ['#login_button', '.login_button', 'button[type="submit"]', 
                                    'input[type="submit"]', 'button:has-text("登录")', 'button.login', 
                                    'a.login', '.login_btn', '[title="登录"]']
            
            # 尝试查找用户名输入框
            username_input = None
            for selector in username_selectors:
                logger.info(f"尝试查找用户名输入框选择器: {selector}")
                if page.locator(selector).count() > 0 and page.locator(selector).is_visible():
                    username_input = page.locator(selector)
                    logger.info(f"找到用户名输入框: {selector}")
                    break
            
            # 尝试查找密码输入框
            password_input = None
            for selector in password_selectors:
                logger.info(f"尝试查找密码输入框选择器: {selector}")
                if page.locator(selector).count() > 0 and page.locator(selector).is_visible():
                    password_input = page.locator(selector)
                    logger.info(f"找到密码输入框: {selector}")
                    break
            
            # 尝试查找登录按钮
            login_button = None
            for selector in login_button_selectors:
                logger.info(f"尝试查找登录按钮选择器: {selector}")
                if page.locator(selector).count() > 0 and page.locator(selector).is_visible():
                    login_button = page.locator(selector)
                    logger.info(f"找到登录按钮: {selector}")
                    break
            
            # 如果找到了所有必要元素，尝试登录
            if username_input and password_input and login_button:
                logger.info("找到所有必要的登录元素，尝试登录")
                
                # 截图记录
                page.screenshot(path=f"data/screenshots/found_login_form_{user_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                # 输入用户名
                logger.info("输入用户名")
                behavior.human_like_typing(
                    username_input, 
                    credentials['email'].split('@')[0]  # QQ邮箱通常只需要输入@前面的部分
                )
                behavior.random_delay()
                
                # 输入密码
                logger.info("输入密码")
                behavior.human_like_typing(
                    password_input, 
                    credentials['password']
                )
                behavior.random_delay()
                
                # 点击登录按钮
                logger.info("点击登录按钮")
                login_button.click()
                
                # 等待页面加载
                page.wait_for_load_state('networkidle')
                behavior.random_delay(2.0, 5.0)
                
                # 检测是否有安全验证
                if "QQ安全中心" in page.title() or page.locator('text=安全验证').count() > 0:
                    logger.warning("检测到安全验证，RBA机制已触发")
                    return {
                        "success": False,
                        "rba_triggered": True,
                        "details": {
                            "用户类型": user_type,
                            "页面标题": page.title(),
                            "登录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "触发项": "安全验证"
                        }
                    }
                else:
                    logger.info("登录成功，未触发RBA机制")
                    return {
                        "success": True,
                        "rba_triggered": False,
                        "details": {
                            "用户类型": user_type,
                            "页面标题": page.title(),
                            "登录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
            else:
                logger.warning("无法找到所有必要的登录元素")
                if not username_input:
                    logger.warning("未找到用户名输入框")
                if not password_input:
                    logger.warning("未找到密码输入框")
                if not login_button:
                    logger.warning("未找到登录按钮")
            
            # 如果所有尝试都失败
            # 创建screenshots目录
            os.makedirs("data/screenshots", exist_ok=True)
            # 保存页面截图
            page.screenshot(path=f"data/screenshots/failed_login_{user_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            logger.error("无法找到登录框或登录按钮，测试失败")
            return {
                "success": False,
                "rba_triggered": False,
                "details": {
                    "用户类型": user_type,
                    "错误": "无法找到登录框或登录按钮"
                }
            }
    
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        return {
            "success": False,
            "rba_triggered": False,
            "details": {
                "用户类型": user_type,
                "错误": str(e)
            }
        }
    finally:
        # 关闭浏览器
        context.close()
        browser.close()

def main():
    """主函数"""
    # 设置环境
    setup_environment()
    # 创建截图目录
    os.makedirs("data/screenshots", exist_ok=True)
    
    # 加载配置
    config = ConfigLoader()
    
    # 设置日志
    logger_config = config.get_logging_config()
    logger = Logger(logger_config)
    
    logging.info("开始QQ邮箱RBA因子测试")
    
    # 获取要测试的场景
    test_scenarios = config.get_test_scenarios()
    
    with sync_playwright() as p:
        # 使用Chromium浏览器进行测试
        
        # 测试正常用户
        if test_scenarios.get('normal_user', True):
            logging.info("开始测试正常用户场景")
            result = perform_login_test(p.chromium, config, "normal")
            logger.log_test_result(
                user_type="正常用户",
                success=result.get('success', False),
                rba_triggered=result.get('rba_triggered', False),
                details=result.get('details', {})
            )
        
        # 测试高风险用户
        if test_scenarios.get('high_risk_user', True):
            logging.info("开始测试高风险用户场景")
            result = perform_login_test(p.chromium, config, "high_risk")
            logger.log_test_result(
                user_type="高风险用户",
                success=result.get('success', False),
                rba_triggered=result.get('rba_triggered', False),
                details=result.get('details', {})
            )
        
        # 测试新设备用户
        if test_scenarios.get('new_device_user', True):
            logging.info("开始测试新设备用户场景")
            result = perform_login_test(p.chromium, config, "new_device")
            logger.log_test_result(
                user_type="新设备用户",
                success=result.get('success', False),
                rba_triggered=result.get('rba_triggered', False),
                details=result.get('details', {})
            )
    
    logging.info("所有测试已完成")

if __name__ == "__main__":
    main()