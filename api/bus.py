import requests
from bs4 import BeautifulSoup
import json
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

refresh_time = 15

# 设置重试策略
retry_strategy = Retry(
    total=3,  # 最大重试次数
    backoff_factor=1,  # 重试间隔
    status_forcelist=[500, 502, 503, 504]  # 需要重试的HTTP状态码
)

# 创建session并设置重试策略
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

def get_bus_info(direction='home'):
    url = "https://atis.taipei.gov.tw/aspx/businfomation/presentinfo.aspx?lang=zh-Hant-TW&ddlName=913"
    
    try:
        response = session.get(url, verify=False, timeout=10)  # 设置10秒超时
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 根據方向選擇不同的div
        div_class = 'bus_go' if direction == 'work' else 'bus_return'
        div = soup.find('div', class_=div_class)
        if not div:
            print(f"未找到 {div_class} div")
            return None
            
        table = div.find('table')
        if not table:
            print(f"未找到表格")
            return None
            
        bus_stops = []
        # 根據方向設置目標站牌
        target_stops = ['及人中學', '十四份', '光華街口'] if direction == 'work' else ["民生敦化路口", "長春敦化路口", "臺北小巨蛋"]
        
        for row in table.find_all('tr'):
            stop_name = row.select_one('td a')
            arrival_time = row.select_one('td:nth-child(2)')
            
            if stop_name and arrival_time:
                stop_name_text = stop_name.text.strip()
                if stop_name_text in target_stops:
                    bus_stops.append({
                        'stop_name': stop_name_text,
                        'arrival_time': arrival_time.text.strip()
                    })
        
        return format_line_message(bus_stops, direction)
    
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        return None

def format_line_message(bus_info, direction):
    if not bus_info:
        return "無法獲取公車資訊"
    
    # 根據方向設置標題
    title = "🚌 搭913上班" if direction == 'work' else "🚌 搭913回家"
    message = f"{title}\n\n"
    for i, stop in enumerate(bus_info):
        message += f"{stop['stop_name']}\n ➡️ {stop['arrival_time']}\n"
    # message += f'\n每{refresh_time}秒更新一次\n輸入\"停\"以停止...'
    return message

if __name__ == "__main__":
    bus_info = get_bus_info('home')
    print(bus_info)
    bus_info = get_bus_info('work')
    print(bus_info)