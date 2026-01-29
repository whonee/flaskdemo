# 建议使用轻量级 Python 镜像
FROM python:3.12-slim

WORKDIR /app

# 复制依赖文件并安装 (利用缓存层)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 生产环境必须安装 gunicorn(only linux) / waitress
RUN pip install waitress

# 复制业务代码
COPY src/ .

# 暴露端口
EXPOSE 5000

# 启动命令 (使用 Gunicorn / waitress 而不是 flask run)
CMD ["waitress-serve", "--port", "5000", "app:create_app"]