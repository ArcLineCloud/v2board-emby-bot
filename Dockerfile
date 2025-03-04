# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 设置时区
RUN ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# 复制项目文件
COPY requirements.txt .
COPY *.py .
COPY .env .

# 创建必要的目录
RUN mkdir -p logs user_data

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 运行机器人
CMD ["python", "main.py"] 