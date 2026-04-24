FROM python:3.11-slim

# 构建参数
ARG SANDBOX_VERSION=1.0.0

# 安装必要的系统包
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置镜像标签
LABEL sandbox.version="${SANDBOX_VERSION}" \
      sandbox.name="ai-learning-platform" \
      maintainer="AI Learning Platform Team" \
      description="Secure sandbox environment for executing Python code"

# 升级pip并安装常用AI库（使用清华镜像加速）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    scikit-learn \
    scipy \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建非root用户
RUN useradd -m -s /bin/bash sandbox && \
    mkdir -p /home/sandbox/tmp && \
    chown -R sandbox:sandbox /home/sandbox

# 设置权限：用户只能写入/tmp目录
RUN chmod 755 /home/sandbox && \
    chmod 1777 /home/sandbox/tmp

# 创建不允许访问的目录列表
RUN mkdir -p /etc/sandbox && \
    echo "/proc\n/sys\n/dev\n/etc\n/bin\n/usr/bin\n/sbin\n/usr/sbin" > /etc/sandbox/forbidden_paths.txt

# 切换为非root用户
USER sandbox
WORKDIR /home/sandbox

# 复制执行脚本
COPY --chown=sandbox:sandbox runner.py /home/sandbox/

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/home/sandbox \
    TMPDIR=/home/sandbox/tmp \
    HOME=/home/sandbox

ENTRYPOINT ["python", "/home/sandbox/runner.py"]
