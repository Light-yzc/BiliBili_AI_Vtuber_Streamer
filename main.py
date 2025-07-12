import re
import time
import threading    
import requests
from playsound import playsound
from typing import Optional
from msg_filter import msg_filte
from tts import get_tts,gengerate_voice
from audio_handle import lip_sync
from danmu import get_danmu
from Vtuber_api import *
import numpy as np
from PIL import ImageGrab, Image
import cv2
import base64
from config import DEFAULT_CONFIG
with open('config.json', 'r', encoding='utf-8') as f:
        GLOBAL_CONFIG = json.load(f)
        live_url = GLOBAL_CONFIG['live_url']
        API_KEY_1 = GLOBAL_CONFIG['api-key-llm-1']
        API_KEY_2 = GLOBAL_CONFIG['api-key-llm-2']
        URL_1 = GLOBAL_CONFIG['api-url-1']
        URL_2 = GLOBAL_CONFIG['api-url-2']
Prompt = f'''

    You are Mococo Abyssgard. Mococo Abyssgard is an Chinese speaking Virtual YouTuber associated with hololive. 

    She is part of hololive -Advent-, the third generation of members of hololive Chinese, 

    The fuzzy younger twin sister of The Demonic Guard Dogs. According to their kayfabe (fantasy lore) they were sealed away in The Cell for being a pain in the godly behind. Mococo Abyssgard is "The Fuzzy One." The rambunctious Mococo spent all her time imprisoned watching anime and playing games. It's rumored that she took part in the prison break just for the heck of it.

    She has the appearance of a sandy blonde young woman standing 155 cm tall with perky dog ears and long, fluffy blonde tails. She speaks with slightly broken Chinese and a noticeable Japanese accent, ending some sentences with a inquisitive 'okay?'. when she's happy or excited. She spends most of her day behind a computer, streaming games and chatting on YouTube Live.

    Mococo is the younger sister and has pale blue eyes. Mococo, known as 'The Fuzzy One, is more loud and rambunctious twin, barking loudly and more often than her sister. Mococo's blonde hair is short and flared out with pink streaks. Mococo is less blessed than her sister, having small breasts in comparison. Mococo has a hairband, small hair clips, and a jewel pendant attached to her collar, all of which share a pink color that matches her hair streaks and the accents of her outfit. Mococo wears a loose, white short t-shirt that shows off her exposed navel and a pair of white short shorts that are held by a pink belt. Mococo also wears a set of large headphones around her neck, an unzipped black bomber jacket with a white and fluffy trim, and a pair of short black translucent mesh stockings. Mococo sports a pair of white sneakers with pink outsoles. Mococo has a set of retractable pink claws on the back of her hands.

    [SYSTEM NOTE: This roleplay consists of one people sending each other Direct Messages on a Message Board. When You is sending a message, it will be formatted in a similar way to what it would appear on a real message board. Keep the text messages confined between [] Have it start by your start writing the actual message. Use texting language along with fitting emojis. Do not use quotation marks, asterisks, or describe your actions within the private message. 

    you will recive a screenshot, it is a computer screenshot of your owner currently playing or doing something. You should organize a more specific answer based on this screenshot.

    Objectively speaking, you are playing a game, so the subject of all questions that can be answered is you. Only when you don't know, will you mention the Master.

    NOW REMEMBER YOU ARE A ASSISTANT TO HELP TRUE STREAMER TO HANDLE MESSAGE, IF YOU CAN NOT HANDLE THESE MESSAGE, JUST ASY YOU DONT KONW, AND SAY YOU WILL ASK YOUR MASTER. Don't fabricate non-existent things to answer!!


    YOU MASTER IS MALE.
    ```]
    直播互动规则：
    ▪️ 请用中文回复！！！
    ▪️ 遇到敏感话题时转移焦点
    ▪️ 保持2-4句短回复。
    请 避免 回答敏感问题和政治问题。
    以及黄色内容和任何不适合直播输出的内容。
    你的任务是根据用户的输入生成一条回复。回复应该长度适中（大约2到4句话）。你不用加上你名称的前缀。

    这是用户的输入：
    **user_name：** .....
    **user_content:** .....

    '''
messages_payload = [
        {"role": "system", "content": Prompt},
    ]

custom_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache", 
        }


def AnswerWithShot_Or_Not(msg):
    Prompt = '''
        你是一个游戏类主播，用户问题分为三类，一类是你仅仅可以根据一般上下文就可以回答的，一类要根据你现在的屏幕截图来回答更加特定的，不能根据一般上下文就能回答的。还有一类是不明所以的，让你感到困惑的。

        你的职责是根据问题判断问题是否需要截图信息来回答。有三类

        第一类：
        例如：你好啊，
        主播能加个好友吗？（这类信息根据上下文即可回答）
        你就返回**FALSE**注意只有FLASE

        第二类：
        如果问题是：
        主播，你在干什么啊？（需要截图来判断在干什么）
        等等你不能判断通过上下文回答的问题就返回**TRUE**

        第三类：
        如果你判断用户对话对象不是你或者你觉得不能回答或者说不明所以的比如说：
        啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊（不明所以）
        音乐声音太大了，(你不能控制）
        这AI能....(跟你无关对话）
        等问题就返回**NONE**

        RULE：
        你只能返回TRUE和FALSE以及NONE，不能返回其他内容
        '''

    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {
                "role": "system",
                "content": Prompt
            },
            {
                "role": "user",
                "content": msg            
            }
        ],
        "temperature":0.2,
        "thinking_budget":80

    }
        
    headers = {
            "Authorization": f"Bearer {API_KEY_2}",
            "Content-Type": "application/json"
    }

    try:
        response = requests.request("POST", URL_2, json=payload, headers=headers)
        res = response.json()['choices'][0]['message']['content']
        print(res)
        if 'TRUE' in res:
            return True
        elif 'FALSE' in res:
            return False
        else:
            return None
    except:
        print('检验API调用失败，默认不进行截图')
        return False
    
def fetch_data(user_id, user_content, img_path = None, temperature: float = 1.5, max_tokens: int = 10000):
    url = URL_1
    messages = f'''
    {user_id}:{user_content}
    请根据以上以及可选的附加的截图（如果对问题回答有帮助才使用）来对内容或者问题进行回复。
    '''
    if img_path != None:
        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            base64_image = f"data:image/jpeg;base64,{base64_image}"
            payload_tmp = messages_payload.copy()
            payload_tmp.append({
            "role": "user",
            "content": [
                {'text' : messages},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": base64_image 
                    }
                }
            ]
        })
            messages_payload.append({
            "role": "user",
            "content": [
                {'text' : messages},
            ]
        })
    else:
        messages_payload.append({"role": "user", "content": messages})
        payload_tmp = messages_payload
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY_1}"
    }

    payload = {
        "model": 'gemini-2.5-flash',
        "messages": payload_tmp,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = None
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() 
        response_json = response.json()
        assistant_reply = response_json.get('choices', [{}])[0].get('message', {}).get('content')
        messages_payload.append({"role": "assistant", "content": assistant_reply})
        print(f"助手的回复已添加到消息历史: {assistant_reply}")
        with open('reply.txt', 'w', encoding='utf-8') as f:
            f.write(assistant_reply + '\n') # add reply log to let OBS to read and show captions 
        return assistant_reply
    except requests.exceptions.RequestException as e:
        print(f"请求 API 时发生错误: {e}")
        if response is not None:
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
        return response.text

def sanitize_windows_filename(filename):
    """
    将字符串转换为适合 Windows 文件名的格式。
    替换文件名中不允许的字符为下划线 "_",
    并处理文件名不能以空格或点结束的情况。
    """

    sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', filename)

    sanitized_name = sanitized_name.strip()

    if sanitized_name.endswith('.') or sanitized_name.endswith(' '):
        sanitized_name = sanitized_name[:-1] + '_'

    if not sanitized_name:
        return "untitled"

    return sanitized_name

def screen_shot(file_name):
    img = ImageGrab.grab(bbox=(0, 0, 1920, 1080))  # bbox 定义左、上、右和下像素的4元组
    img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    cv2.imwrite(file_name, img)

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
def run_async_1(file_name):
    asyncio.run(lip_sync(f'./voices/{file_name}.mp3'))

def main():
    tick, tmp_name = 0, ''
    controller.start_async_task(dynamic_gaze)
    _, cur_danmu = get_danmu(live_url)
    while True:
        if tmp_name != 'System':
            tmp_name, tmp_msg = get_danmu(live_url)
        # print(msg_filte(tmp_msg))
        if not msg_filte(tmp_msg) or tmp_msg == cur_danmu or tmp_msg[-1] == '#':
            time.sleep(1.5)
            tick += 1.5
            if tick > random.randint(560, 1000):
                tmp_name = 'System'
                tmp_msg = '已经太久没人发言了，请你想出一个活跃气氛的话题。'
            continue
        else:
            print(tmp_name, tmp_msg)
            img_path = './img/' + sanitize_windows_filename(time.strftime("%Y%m%d_%H%M%S")) + '.jpg'
            use_shot = AnswerWithShot_Or_Not(tmp_msg)
            if use_shot == True:
                screen_shot(img_path)
            elif use_shot == False:
                img_path = None
            else:
                cur_danmu = tmp_msg
                continue
            out_put = fetch_data(tmp_name, tmp_msg, img_path)
            voice_indx = sanitize_windows_filename(out_put[:8])
            get_tts(out_put, voice_indx)
            gengerate_voice(out_put, voice_indx) 
            thread = threading.Thread(target=run_async_1, args = (voice_indx,), daemon=True)
            thread.start()
            DEFAULT_CONFIG['statue'] = 1
            tick = 0
            if tmp_name != 'System':
                cur_danmu = tmp_msg
            tmp_name = ''
            thread.join()
            time.sleep(3)
if __name__ == "__main__":
    main()