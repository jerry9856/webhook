from flask import Flask, request, jsonify
try:
    # 嘗試相對導入（用於 Vercel 部署）
    from .message_handlers import send_youtube_url, send_now, send_prompt, send_bus_info, send_weather_info
    from .utils import send_message
    from .bus import get_bus_info, refresh_time
except ImportError:
    from message_handlers import send_youtube_url, send_now, send_prompt, send_bus_info, send_weather_info
    from utils import send_message
    from bus import get_bus_info, refresh_time

import threading
import time

app = Flask(__name__)

# 儲存使用者的計時器狀態
user_timers = {}

def start_bus_timer(user_id, direction):
    def timer_function():
        while user_id in user_timers and user_timers[user_id]:
            send_bus_info(user_id, direction)
            time.sleep(refresh_time)
    
    # 如果已經有定時器在運行，先停止它
    if user_id in user_timers:
        user_timers[user_id] = False
        time.sleep(1)  # 等待之前的定時器停止
    
    # 啟動新的定時器
    user_timers[user_id] = True
    timer_thread = threading.Thread(target=timer_function)
    timer_thread.daemon = True
    timer_thread.start()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    for event in data['events']:
        user_id = event['source']['userId']
        message_text = event['message']['text']

        if message_text.startswith('yt'):
            send_youtube_url(user_id, message_text)
        elif message_text.startswith('now'):
            send_now(user_id)
        elif message_text.startswith('回家'):
            # start_bus_timer(user_id, 'home')
            send_bus_info(user_id, 'home')
        elif message_text.startswith('上班'):
            # start_bus_timer(user_id, 'work')
            send_bus_info(user_id, 'work')
        # elif message_text == '停':
        #     if user_id in user_timers:
        #         user_timers[user_id] = False
        #         send_message(user_id, "已停止公車資訊更新")
        elif message_text.startswith('天氣'):
            send_weather_info(user_id)
        else:
            send_prompt(user_id)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run()
