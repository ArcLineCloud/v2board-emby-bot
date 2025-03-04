# v2board-emby-bot

## 安装要求

- Python 3.11
- Docker（如果使用 Docker 部署）

## 配置说明

1. 复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填写以下配置：

```plaintext
# V2Board API配置，如果你的主网址是https://xxxx.xx，一般填写https://api.xxxx.xx/api/v1
V2BOARD_URL=https://api.xxxx.xx/api/v1

# Telegram Bot配置
TELEGRAM_BOT_TOKEN=your-bot-token

# Emby配置
EMBY_URL=http://your-emby-url/
EMBY_API_KEY=your-emby-api-key

# 允许创建Emby账号的订阅等级列表，多个等级用英文逗号分隔
ALLOWED_PLAN_IDS=2,3,4,5

# 给用户登录的emby服务器地址模板，多行字符串，换行符为\n
EMBY_SERVER_URL_TEMPLATE="大陆线路：https://cn.your-emby.com/\n香港线路：https://hk.your-emby.com/\n日本线路：https://jp.your-emby.com/"
```

## 安装方法

### 方法一：直接运行（推荐开发环境使用）

1. 解压代码：

```bash
unzip plane-to-emby.zip
cd plane-to-emby
```

2. 创建虚拟环境（可选）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 运行机器人：

```bash
python main.py
```

**注意：此方法不能关闭终端，否则机器人会停止运行（或者使用 screen 解决）**

### 方法二：Docker 部署

1. 解压代码：

```bash
unzip plane-to-emby.zip
cd plane-to-emby
```

2. 构建并启动容器：

```bash
docker-compose up -d
```

3. 查看日志：

```bash
docker-compose logs -f
```

## 目录结构

```
.
├── main.py              # 主程序
├── emby_api.py         # Emby API 封装
├── v2board_api.py      # V2Board API 封装
├── scheduler.py        # 定时任务
├── requirements.txt    # Python 依赖
├── .env               # 环境配置
├── Dockerfile         # Docker 构建文件
├── docker-compose.yml # Docker 编排配置
├── logs/             # 日志目录
└── user_data/        # 用户数据目录
```

## 使用说明

1. 在 Telegram 中搜索你的机器人并启动
2. 使用 `/start` 命令开始使用
3. 使用 `/help` 查看所有可用命令
4. 使用 `/login` 登录你的账号

可用命令列表：

- `/start` - 开始使用机器人
- `/help` - 显示帮助信息
- `/login` - 登录账号
- `/info` - 查看账户信息
- `/subscribe` - 获取订阅信息
- `/plans` - 查看可用套餐
- `/orders` - 查看订单列表
- `/create_emby` - 创建 Emby 账号
- `/emby_info` - 查看 Emby 账号信息
- `/delete_emby` - 删除 Emby 账号

## 维护说明

### 日志管理

- 日志文件位于 `logs` 目录
- 每天自动分割日志文件
- 自动删除 30 天前的日志

### 数据备份

建议定期备份以下目录：

- `user_data/` - 用户数据
- `logs/` - 日志文件

### Docker 维护

```bash
# 更新镜像
docker-compose pull

# 重新构建
docker-compose build --no-cache

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 常见问题

1. 如何更新 Bot Token？

   - 修改 `.env` 文件中的 `TELEGRAM_BOT_TOKEN`
   - 重启服务

2. 如何修改允许的订阅等级？

   - 修改 `.env` 文件中的 `ALLOWED_PLAN_IDS`
   - 重启服务
