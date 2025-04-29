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
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# 讀取 prompt.json
if os.path.exists('prompt.json'):
    with open('prompt.json', 'r', encoding='utf-8') as f:
        prompt = json.load(f)
elif os.path.exists('../prompt.json'):
    with open('../prompt.json', 'r', encoding='utf-8') as f:
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

def send_image(user_id, image_url):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    message_data = {
        "to": user_id,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url
            }
        ]
    }

    response = requests.post(url, headers=headers, json=message_data)
    return response

def get_weather_data():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Taipei",
        "units": "metric",
        "lang": "zh_tw",
        "appid": WEATHER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 檢查是否有錯誤
        data = response.json()
        
        # 格式化輸出
        message = f"地點：{data['name']}\n"
        message += f"溫度：{data['main']['temp']}°C\n"
        message += f"體感溫度：{data['main']['feels_like']}°C\n"
        message += f"天氣狀況：{data['weather'][0]['description']}"
        # message += f"濕度：{data['main']['humidity']}%\n"
        # message += f"風速：{data['wind']['speed']} m/s\n"
        # message += f"icon：{data['weather'][0]['icon']}\n"
        iconUrl = f"https://openweathermap.org/img/w/{data['weather'][0]['icon']}.png"
        return [message, iconUrl]
    except requests.exceptions.RequestException as e:
        print(f"獲取天氣數據時發生錯誤：{e}")
        return None

def make_prompt():
    prompt_text = "你可以輸入這些：\n"
    for p in prompt:
        prompt_text += f"{p['text']}：{p['example']}\n"
    return prompt_text 