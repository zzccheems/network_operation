# 基础镜像
FROM python:3.9-slim
# 设置工作目录
WORKDIR /app
# 复制项目文件
COPY . /app
# 安装依赖库
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 暴露Web端口
EXPOSE 5000
# 启动主程序
CMD ["python", "main.py"]