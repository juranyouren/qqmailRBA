# QQ邮箱RBA因子黑盒测试工具

## 项目概述
本项目旨在通过模拟不同用户行为模式（登录频率、设备指纹、地理位置、操作行为等），触发QQ邮箱的基于风险的认证（RBA）机制，从而分析其风险因子判断逻辑。

## 目录结构
- `src/`: 源代码目录
- `tests/`: 测试代码目录
- `config/`: 配置文件目录
- `utils/`: 工具函数库
- `data/`: 数据存储目录

## 主要功能
1. 模拟不同的虚拟身份（正常用户、高风险用户、新设备用户）
2. 自定义设备指纹和用户行为
3. 代理IP管理
4. RBA触发检测与日志记录
5. 数据分析与可视化

## 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

## 使用方法
1. 配置测试账号与参数
```bash
cp config/config.example.ini config/config.ini
# 编辑config.ini填入测试账号信息
```

2. 运行测试
```bash
python src/main.py
```

## 注意事项
- 本工具仅用于安全研究目的，请勿用于非法活动
- 仅测试自有账号，避免侵犯他人隐私
- 需遵守QQ邮箱服务条款
