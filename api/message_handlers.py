from datetime import datetime
from utils import search_youtube, send_message, make_prompt
from bus import get_bus_info

def send_youtube_url(user_id, message_text):
    search_query = message_text[2:].strip()
    video_url = search_youtube(search_query)
    if video_url:
        send_message(user_id, f"{video_url}")
    else:
        send_message(user_id, "抱歉，找不到相關影片。")

def send_now(user_id):
    send_message(user_id, f"現在時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def send_bus_info(user_id, direction='home'):
    bus_info = get_bus_info(direction)
    send_message(user_id, bus_info)

def send_prompt(user_id):
    send_message(user_id, make_prompt()) 