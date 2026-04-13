FROM python:3.12-slim

# Install System Packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set WORKDIR
WORKDIR /one_piece

# 1. uv 설치 + PATH 등록을 한 번에
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

# 2. uv 설정 (uv는 기본적으로 가상환경을 만들려고 하지만,
# 도커 컨테이너 자체를 환경으로 쓰려면 시스템에 직접 설치하도록 설정합니다)
ENV UV_PROJECT_ENVIRONMENT="/usr/local"

# 3. 설정 파일 복사
COPY ../../pyproject.toml uv.lock ./

# 4. 의존성 설치 (uv는 'install'이 아니라 'sync'를 사용합니다)
# --no-cache를 넣어주면 이미지 용량이 줄어듭니다.
RUN uv sync --no-cache

# 5. 프로젝트 파일 복사
COPY ../.. .