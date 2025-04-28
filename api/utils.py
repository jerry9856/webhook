import os
import requests
import json
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv

# 檢查.env檔案是否存在
if os.path.exists('../.env'):
    load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# 讀取 prompt.json
if os.path.exists('prompt.json'):
    with open('prompt.json', 'r') as f:
        prompt = json.load(f)
elif os.path.exists('../prompt.json'):
    with open('../prompt.json', 'r') as f:
        prompt = json.load(f)
else:
    prompt = []

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