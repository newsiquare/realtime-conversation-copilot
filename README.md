## realtime-conversation-copilot
用 Flask 串接 ollama 及 Faster Whisper， 產生 Web-service

![image](https://github.com/newsiquare/realtime-conversation-copilot/blob/main/introduction.jpg)

### 環境安裝
pip install flask, flask-restful, replicate, boto3, ollama
  
  
### 本機安裝 ollama
https://ollama.com/download/


### 執行
```
python app.py
```

#### (option) 執行 - 多人
```
gunicorn --workers=4 --threads=4 wsgi:app
```

### API 測試
```
http://.../api/v1/test
```
