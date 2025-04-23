import time
import threading    
import requests
from playsound import playsound
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from typing import Optional
from msg_filter import msg_filte
from tts import get_tts
from audio_handle import lip_sync
from danmu import get_danmu
from Vtuber_api import *
from config import GLOBAL_CONFIG
char_id = 1
# 注册插件
live_url = 'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid=1862819&room_type=0'
msg_i = ''
turns = 1
data = {}
re_format = '<thinking>(.*?)</thinking>'
i = 0
def browser_gen():
    service = Service(r'./driver/msedgedriver.exe') 
    options = webdriver.EdgeOptions() # 创建一个配置对象
    #options.add_argument("--headless") # 开启无界面模式
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1000")    
    options.add_experimental_option("detach", True)
    # browser = webdriver.Edge(service=service, options=options)

    browser = webdriver.Edge(service=service, options=options)
    browser.set_window_size(1920, 1000)
    browser.get("http://127.0.0.1:8000/")
    time.sleep(4)
    element = browser.find_element(By.ID, "rightNavHolder")
    ActionChains(browser).move_to_element(element).click().perform()
    time.sleep(1)
    elm2 =browser.find_element(By.ID,"CharID1")
    ActionChains(browser).move_to_element(elm2).click().perform()
    return browser


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Length": "115",
    "Content-Type": "application/json",
    "Cookie": "session-1a528558=eyJjc3JmVG9rZW4iOiI2MjRjNzc0MDY5NGFhYmVkMDFmNWFlNTFjMjhjNWU5OGY1MGJhOTk3NWMxZmFmNmFjYjE1MzY5Njc2NDk0NzBhIn0=; session-1a528558.sig=1Qi0qTA0SBu9lmwU0NgXhUcYXmA",
    "Host": "127.0.0.1:8000",
    "Origin": "http://127.0.0.1:8000",
    "Sec-Ch-Ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
    "X-Csrf-Token": "624c7740694aabed01f5ae51c28c5e98f50ba9975c1faf6acb1536967649470a",
    "X-Requested-With": "XMLHttpRequest"
}



# if turns == 1:
#     global browser
#     browser  = browser_gen()
#     # <div class="flex-container swipeRightBlock flexFlowColumn flexNoGap">
#     #                 <div class="swipe_right fa-solid fa-chevron-right interactable" style="display: flex; opacity: 0.7;" tabindex="0"></div>
#     #                 <div class="swipes-counter" style="opacity: 0.7;">1&ZeroWidthSpace;/&ZeroWidthSpace;1</div>
#     #             </div>
#     try:
#         xpath_expression = "//div[@class='flex-container swipeRightBlock flexFlowColumn flexNoGap']/div[@class='swipe_right fa-solid fa-chevron-right interactable' and @style='display: flex; opacity: 0.3;' and @tabindex='0']"
#         elm1 = browser.find_element(By.XPATH,xpath_expression)
#     except:
#         xpath_expression = "//div[@class='flex-container swipeRightBlock flexFlowColumn flexNoGap']/div[@class='swipe_right fa-solid fa-chevron-right interactable' and @style='display: flex; opacity: 0.7;' and @tabindex='0']"
#         elm1 = browser.find_element(By.XPATH,xpath_expression)
#     ActionChains(browser).move_to_element(elm1).click().perform()



def get_date(num):
    global headers,browser
    url = 'http://127.0.0.1:8000/api/characters/all'

    data = {
                '':''
            }

    res = requests.post(url = url, headers = headers,json=data)
    msg = { 
        'avatar_url':res.json()[num]['avatar'],
        'file_name':res.json()[num]['chat'],
        'ch_name':res.json()[num]['name']
    }
    return msg



data = {}


def get_msg(num):
        global data
        url = 'http://127.0.0.1:8000/api/chats/get'
        if turns == 1:
            data = get_date(num)
        res = requests.post(url = url, headers = headers,json=data)
        msg = res.json()[-1]['mes']
        return msg


def del_msg():
    global browser
    elm5 = browser.find_element(By.ID,'options_button')
    ActionChains(browser).move_to_element(elm5).click().perform()
    elm6 = browser.find_element(By.ID,'option_start_new_chat')
    ActionChains(browser).move_to_element(elm6).click().perform()
    time.sleep(1)
    try:
        elm7 = browser.find_element(By.ID,'del_chat_checkbox')
    except:
        elm7 = browser.find_element(By.ID,"//input[@id='del_chat_checkbox']")
    ActionChains(browser).move_to_element(elm7).click().perform()
    xpath_expression = "//div[contains(@class, 'popup-button-ok') and contains(@class, 'menu_button') and contains(@class, 'result-control') and contains(@class, 'menu_button_default') and contains(@class, 'interactable')]"
    elm8 = browser.find_element(By.XPATH,xpath_expression)
    ActionChains(browser).move_to_element(elm8).click().perform()


def init_chat():
    global turns
    del_msg()
    time.sleep(2)
    try:
        xpath_expression = "//div[@class='flex-container swipeRightBlock flexFlowColumn flexNoGap']/div[@class='swipe_right fa-solid fa-chevron-right interactable' and @style='display: flex; opacity: 0.3;' and @tabindex='0']"
        elm1 = browser.find_element(By.XPATH,xpath_expression)
        ActionChains(browser).move_to_element(elm1).click().perform()

    except:
        xpath_expression = "//div[@class='flex-container swipeRightBlock flexFlowColumn flexNoGap']/div[@class='swipe_right fa-solid fa-chevron-right interactable' and @style='display: flex; opacity: 0.7;' and @tabindex='0']"
        elm1 = browser.find_element(By.XPATH,xpath_expression)
        ActionChains(browser).move_to_element(elm1).click().perform()
    turns = 1

    

if turns != 1:
    msg_i = get_msg(char_id)  






def excut_msg(browser,message):
    global msg_i,turns,api_used
    if turns == 1:
        init_msg = get_msg(char_id)
        msg_i = init_msg
        turns += 1
        return '------------------初始信息-------（你看到这条消息就意味着你发的消息不管用，要再发一条才算正式开始对话，这条只是对对话背景的补充）\n' + init_msg
    i = 1
    # browser = open_broser()
    # 如果在send_msg之前get一下会不会好点?
    msg_i = get_msg(char_id)
    elm3 = browser.find_element(By.ID,'send_textarea')
    elm3.send_keys(message)
    elm4 = browser.find_element(By.ID,'send_but')
    ActionChains(browser).move_to_element(elm4).click().perform()
    msg = get_msg(char_id)
    turns += 1
    while msg_i == msg or msg == message:
        i += 1
        time.sleep(0.5)
        msg = get_msg(char_id)
        if i > 360:
            return '酒馆未响应，可能是因为Api路线问题或者额度没了'
    # msg_i = msg
    # browser.close()
    if i > 80:
        return msg + '\n****当前Api请求过慢，可能因为供应商服务器负载过大\n请过一会重新初始化后再次尝试****'
    return msg
msg_to_change_char = 'CharID0  名称：两只亡灵少女   描述：无\nCharID1  名称：Freya   描述：雨中坠落的天使…….\nCharID2  名称：Miki   描述：文风比较独特\nCharID3  名称：Saber   描述：解决Saber泛滥的社会问题的Saber\nCharID4  名称：Queen   描述：异.....异形？\nCharID5 名称：Tiche   描述：抢走你牛至的魔法少女！\nCharID6  名称：伊蕾娜   描述：欢迎来到魔女的世界！\nCharID7  名称：呕吐内心的少女   描述：无\nCharID8  名称：娘化生物世界   描述：无\nCharID9  名称：帝国拷问官   描述：无\nCharID10  名称：扫一扫   描述：扫一扫更改数据\nCharID11  名称：末世孤雄RPG   描述：无\nCharID12  砂狼白子   描述：欢迎来到碧蓝档案！\nCharID13  名称：芙蕾雅   描述：雨中坠落的天使…….\nCharID14  名称：虚拟色色体验馆   描述：无\n如果报错请重新切换角色或者初始化'



def change_character(ch_id):
    global turns
    element = browser.find_element(By.ID, "rightNavHolder")
    ActionChains(browser).move_to_element(element).click().perform()
    time.sleep(1)
    elm2 = browser.find_element(By.XPATH,"//div[@title='选择/创建角色']")
    ActionChains(browser).move_to_element(elm2).click().perform()
    elm2 =browser.find_element(By.ID,ch_id)
    ActionChains(browser).move_to_element(elm2).click().perform()
    # turns = 1 is the pro?
    turns = 2


def format_str(text):
    # # return text
    # global re_format
    # matches = re.findall(re_format, text, re.DOTALL)
    # # if len(matches) == 0:
    # #     return text
    # return  [s.strip() for s in re.split(r'\s*/\s*', text) if s.strip()]
# -----------------
    return text


class AsyncController:
    def __init__(self):
        self.current_loop: Optional[asyncio.AbstractEventLoop] = None
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

    def start_async_task(self, coro_func):
        """启动新的异步任务并停止之前的任务"""
        # 停止当前任务
        self.stop_current_task()
        
        # 创建新事件循环
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._run_async, 
            args=(coro_func,),
            daemon=True
        )
        self.thread.start()

    def _run_async(self, coro_func):
        """在新线程中运行异步任务"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.current_loop = loop
        
        try:
            loop.run_until_complete(
                self._wrap_coroutine(coro_func)
            )
        finally:
            loop.close()
            self.current_loop = None

    async def _wrap_coroutine(self, coro_func):
        """包装协程以响应停止事件"""
        task = asyncio.create_task(coro_func())
        while not self.stop_event.is_set():
            await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def stop_current_task(self):
        """停止当前运行的异步任务"""
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=1)
            if self.current_loop:
                self.current_loop.call_soon_threadsafe(
                    self.current_loop.stop
                )

# 实例化全局控制器
controller = AsyncController()
def run_async_1():
    asyncio.run(lip_sync(r"D:\Code\vtuber\voices\1.mp3"))

def main():
    # global i
    controller.start_async_task(dynamic_gaze)
    browser  = browser_gen()
    element = browser.find_element(By.ID, "ai-config-button")
    ActionChains(browser).move_to_element(element).click().perform()
    out_put = format_str(excut_msg(browser, '1'))
    cur_danmu = get_danmu(live_url)

    while True:
        if msg_filte(get_danmu(live_url)) or danmu == cur_danmu:
            time.sleep(1)
            continue
        danmu = get_danmu(live_url)
        # if danmu == cur_danmu and i != 0:
        #     time.sleep(1)
        #     continue
        out_put = format_str(excut_msg(browser, danmu))
        print(out_put)
        get_tts(out_put)
        thread = threading.Thread(target=run_async_1, daemon=True)
        thread.start()
        GLOBAL_CONFIG['statue'] = 1
        cur_danmu = danmu
        # i+=1
        thread.join()
        time.sleep(3)
if __name__ == "__main__":
    # 主线程也需要事件循环
    # asyncio.run(main())
    main()