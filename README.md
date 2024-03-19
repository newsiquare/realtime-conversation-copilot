realtime-conversation-copilot
~ 使用 Flask 串接 ollama 及 Faster Whisper， 產生 Web-service

# 環境安裝
pip install flask, flask-restful, replicate, boto3, ollama

# 本機安裝 ollama
https://ollama.com/download/

# 執行
python app.py

# (option) 執行 - 多人
gunicorn --workers=4 --threads=4 wsgi:app


# API 測試
../api/v1/test
