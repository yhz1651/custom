import requests
import time
import json
from loguru import logger

logger.add("./log/app.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level="DEBUG")
session = requests.Session()


def chat_with_requests(url, model, message, max_retries=3):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer "  # 替换为你的API密钥
    }
    data = {
        "model": model,
        "messages": message
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = session.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                error_msg = f"Attempt {attempt}/{max_retries} failed: {response.content}"
                logger.error(error_msg)
                time.sleep(2 ** attempt)
        except Exception as e:
            error_msg = f"Attempt {attempt}/{max_retries} failed: {str(e)}"
            logger.error(error_msg)
            time.sleep(2 ** attempt)

if __name__ == '__main__':
    url = "http://100.100.20.144:9997/v1/chat/completions"
    model = "qwen3"
    messages = [
        {'role': 'system', 'content': "you are a helpful assistant"},
        {'role': 'user', 'content': "1+1="}
    ]
    content = chat_with_requests(url, model, messages)
    print(content)