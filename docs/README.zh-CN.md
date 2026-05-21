# Flask Gym 平台说明（中文）

## 1. 项目简介

这是一个基于 Flask 的健身房管理平台，包含三类角色：

- 会员（Customer）：注册、资料维护、课程查看与报名
- 教练（Coach）：资料维护、课程发布
- 管理员（Manager）：后台管理用户与课程

本次已完成开源化改造：

- 将敏感配置改为环境变量
- 默认使用 SQLite，降低本地启动门槛
- 移除或替换可识别的个人信息

## 2. 当前架构

为了保留历史版本的功能逻辑，当前仍采用单体结构：

- app/__init__.py：应用与扩展初始化
- app/model.py：数据库模型与用户加载
- app/routes.py：业务路由与角色流程
- app/forms.py：表单定义
- app/templates：前端模板
- app/static：静态资源

## 3. 配置说明

配置统一在 config/settings.py 的 Config 类中，优先读取环境变量。

核心变量：

- SECRET_KEY
- DATABASE_URL
- MAIL_SERVER / MAIL_PORT / MAIL_USERNAME / MAIL_PASSWORD / MAIL_DEFAULT_SENDER

## 4. 本地启动（Windows）

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item configs/env.example .env
python scripts/db_create.py
python run.py
```

浏览器访问：http://127.0.0.1:5000

## 5. 脱敏内容

已完成以下脱敏：

- 删除硬编码密钥、数据库账号、邮箱凭据
- 邮件发送地址改为 MAIL_DEFAULT_SENDER
- 测试中的真实邮箱替换为 example.com

建议：如果历史提交中出现过真实密钥，公开前务必在对应服务端执行轮换。

## 6. 你可以如何讲解这个项目

面试或答辩时可以强调：

- 为什么要把配置和代码解耦（12-factor 思路）
- 为什么默认 SQLite（可运行优先，便于 reviewer 快速验证）
- 如何从历史单体项目升级为可公开维护的开源项目
- 后续如何拆分蓝图、补充 CI、完善测试夹具
