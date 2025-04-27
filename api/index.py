import os
import requests
import json
from flask import Flask, request, jsonify
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv

app = Flask(__name__)

# 檢查.env檔案是否存在
if os.path.exists('../.env'):
    load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# 讀取 prompt.json
with open('../prompt.json', 'r') as f:
    prompt = json.load(f)

def search_youtube(query):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

# 發送訊息的函數
def send_message(user_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    message_data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, json=message_data)
    return response

def make_prompt():
    prompt_text = "你可以輸入這些：\n"
    for p in prompt:
        prompt_text += f"{p['text']}：{p['example']}\n"
    return prompt_text

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # 確保只有當用戶發送特定訊息時，才回應
    for event in data['events']:
        user_id = event['source']['userId']
        message_text = event['message']['text']

        if message_text.startswith('yt'):
            search_query = message_text[2:].strip()
            video_url = search_youtube(search_query)
            if video_url:
                send_message(user_id, f"{video_url}")
            else:
                send_message(user_id, "抱歉，找不到相關影片。")
        elif message_text.startswith('now'):
            send_message(user_id, f"現在時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            send_message(user_id, make_prompt())

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run()
