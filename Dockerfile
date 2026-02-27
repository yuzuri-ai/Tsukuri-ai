FROM python:3.11-slim

# OpenSCADのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openscad \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ordersディレクトリを作成
RUN mkdir -p /app/orders

# ポート設定（Railwayが$PORTを注入する）
EXPOSE 8501

# Streamlitの設定
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# OpenSCADを仮想ディスプレイ付きで動かすため
ENV DISPLAY=:99

# 起動コマンド
CMD Xvfb :99 -screen 0 1024x768x16 & \
    streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true
