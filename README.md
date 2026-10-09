# MailSystem

一个基于 Django 4.2 的简单邮件管理系统，支持邮件发送、QQ 邮箱收取、联系人、星标、回收站、附件和个人资料管理。

## 环境要求

- Python 3.8 或更高版本
- 可用的 QQ 邮箱账号和邮箱授权码（需要收发真实邮件时）

## 安装

```powershell
git clone https://github.com/Loforfree/MailSystem.git
cd MailSystem

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

如果 PowerShell 禁止运行激活脚本，可以不激活虚拟环境，直接使用：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

## 邮箱配置

邮箱账号和授权码不要填写到 `mail_manger/settings.py`，也不要提交到 GitHub。项目从系统环境变量读取连接信息。根目录的 `.env.example` 仅用于查看所需参数，当前项目不会自动读取 `.env` 文件。

在启动网站的同一个 PowerShell 窗口中设置 QQ 邮箱参数：

```powershell
$env:EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST = "smtp.qq.com"
$env:EMAIL_PORT = "465"
$env:EMAIL_USE_SSL = "true"
$env:EMAIL_USE_TLS = "false"
$env:EMAIL_HOST_USER = "你的QQ邮箱地址"
$env:EMAIL_HOST_PASSWORD = "你的QQ邮箱授权码"
```

`EMAIL_HOST_PASSWORD` 应填写邮箱授权码，不是 QQ 登录密码。需要先在 QQ 邮箱设置中启用 SMTP 和 IMAP 服务并生成授权码。

当前“收取邮件”功能固定连接 `imap.qq.com:993`，因此只适用于 QQ 邮箱。SMTP 参数只控制邮件发送。

不配置邮箱参数时，系统默认使用 Django 控制台邮件后端：邮件不会真正发出，内容只会显示在运行服务器的终端中。

### Django 密钥

本地调试可以不设置 `DJANGO_SECRET_KEY`，程序会临时生成。部署到服务器时必须使用固定随机值：

```powershell
$env:DJANGO_SECRET_KEY = "请替换为随机且保密的长字符串"
```

## 初始化和运行

首次运行需要创建数据库表：

```powershell
python manage.py migrate
```

如需使用 Django 后台，可创建管理员账号：

```powershell
python manage.py createsuperuser
```

启动本地开发服务器：

```powershell
python manage.py runserver
```

浏览器访问：

- 邮件系统：<http://127.0.0.1:8000/>
- Django 后台：<http://127.0.0.1:8000/admin/>

## 数据与隐私

- 本地数据保存在 `db.sqlite3`，该文件已被 Git 忽略。
- 收取的附件保存在 `media/email_attachments/`，附件内容已被 Git 忽略。
- `.env`、数据库、附件、Python 缓存和虚拟环境不会进入版本库。
- 如果授权码曾被公开或提交到 Git，应立即到邮箱后台撤销并重新生成。

本项目使用 Django 开发服务器，仅适合本地调试，不应直接用于生产环境。
