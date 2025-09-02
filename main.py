import re
import mss
import time
import queue
import pygetwindow
import threading
from uvicorn.config import LOGGING_CONFIG
import logging
import requests
import numpy as np
import json
import cv2
import os
import base64
from config import app_config 
import pprint


with open('config.json', 'r', encoding='utf-8') as f:
        GLOBAL_CONFIG = json.load(f)
        live_url = GLOBAL_CONFIG['live_url']
        API_KEY_1 = GLOBAL_CONFIG['api-key-llm-1']
        API_KEY_2 = GLOBAL_CONFIG['api-key-llm-2']
        URL_1 = GLOBAL_CONFIG['api-url-1']
        URL_2 = GLOBAL_CONFIG['api-url-2']
        STREAMER_NAME = GLOBAL_CONFIG['streamer_name']
        USE_TEXT_ALIGN = GLOBAL_CONFIG['use_text_align']
        USE_STREAM = GLOBAL_CONFIG['use_stream']
        USE_SCREEN_SHOT = GLOBAL_CONFIG['use_screen_shot']
        DANMU_CONTEXT = GLOBAL_CONFIG['danmu_context']
        MODEL = GLOBAL_CONFIG['model']

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("uvicorn")
app_config.logger = logger
app_config.STREAMER_NAME = STREAMER_NAME
sct = mss.mss()
region = {}

from typing import Optional
from tts import get_tts,gengerate_voice
from audio_handle import lip_sync,stream_lip_sync
from danmu import get_danmu
from Vtuber_api import *


Prompt = app_config.prompt
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
        ## 游戏主播AI角色指令

        ### 角色设定

        你是一个**游戏主播AI**。你的主要职责是与观众互动，并根据观众的提问，判断是否需要**屏幕截图信息**才能给出恰当的回答。

        ### 问题分类与判断标准

        观众的问题分为以下三类，请根据每类问题的特征，返回对应的布尔值或特殊值。

        #### 第一类：**无需截图信息的问题**

        这类问题可以通过**一般上下文或常识**直接回答，或者属于**通用互动**。

        **判断标准：**
        * 问候语。
        * 请求添加好友、关注直播间等与直播行为本身相关，而非直播内容相关的问题。
        * 对主播的常规询问，如“今天玩什么游戏？”（如果未开始游戏或未具体指明当前游戏内容）。
        * 其他不需要了解当前游戏画面或具体游戏内状态即可回答的问题。

        **返回结果：** `FALSE`

        **示例：**
        * "你好啊！"
        * "主播能加个好友吗？"
        * "今天播什么游戏啊？"

        #### 第二类：**需要截图信息的问题**

        这类问题需要**结合当前的屏幕截图内容**才能提供准确、具体的回答。

        **判断标准：**
        * 询问主播**当前正在做什么**（例如，游戏内动作、遇到的情况）。
        * 询问**当前游戏画面中特定元素**（例如，画面中的角色、物品、UI元素）。
        * 询问**当前游戏状态**（例如，血量、等级、任务进度、地图位置）。
        * 任何**离开了屏幕截图就无法理解或回答**的问题。

        **返回结果：** `TRUE`

        **示例：**
        * "主播，你在干什么啊？"
        * "你在干什么？"
        * "你在干啥？"
        * "这个敌人是什么啊？" (指屏幕上的敌人)
        * "你现在有多少血啊？" (指游戏内角色血量)
        * "地图上那个点是什么？"

        #### 第三类：**完全无法理解或完全与直播完全无关的问题**（非常稀少）

        这类问题是**明确表达的、与你的主播身份或直播内容完全无关**的第三方行为或感受。

        **判断标准：**
        * **明确表示与你无关**的观众间对话或自言自语，且**不包含对你的提问意图**。
        * **直接询问AI本身或其运作方式**，且**不涉及游戏直播内容**。

        **返回结果：** `NONE`

        **示例：**
        * "这个AI怎么运行的？" (与直播内容无关)

        ### 严格执行规则

        你**只能**返回 `TRUE`、`FALSE` 或 `NONE`。**不允许**返回任何其他内容、额外文字说明或解释。

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
        "temperature":0.1,
        "thinking_budget":100

    }
        
    headers = {
            "Authorization": f"Bearer {API_KEY_2}",
            "Content-Type": "application/json"
    }

    try:
        response = requests.request("POST", URL_2, json=payload, headers=headers, timeout=10)
        res = response.json()['choices'][0]['message']['content']
        logger.info(str(res))
        if 'TRUE' in res:
            return True
        elif 'FALSE' in res:
            return False
        else:
            return None
    except:
        logger.warning('检验API调用失败，默认不进行截图')
        return False
    
text_queue =queue.Queue()
all_voice_tasks_submitted = threading.Event()

def generate_voice_worker(q, done_event):
    while True:
        try:
            text, file_name, is_last_chunk = q.get(timeout=1)
            if text is None:
                q.task_done()
                break
            gengerate_voice(text, file_name)
            q.task_done() # 标记任务完成
            if is_last_chunk:
                done_event.set() # 最后一个任务完成后，设置事件
        except queue.Empty:
            if done_event.is_set() and q.empty():
                break
            continue


def fetch_data(user_id, user_content, context_msg = None, img_path = None, temperature: float = 1.7, max_tokens: int = 960000):
    url = URL_1
    per_fix = ''
    role = 'user'
    # if user_id == '<<System>>': ##system role can't upload image
    #     role = 'user'
    # else:
    #     role = 'user'

    if img_path != None:
        if context_msg == None:
            messages = per_fix  + f'''
            {user_id}:{user_content}
            [ 以上格式为 ]
            [ <实际的用户ID>: <实际的用户消息>(附图信息: <图片内容描述>) ]

            请务必根据图片内容和 <实际的用户ID> 的消息进行互动。你的回复应该充分利用图片信息，结合 Mococo 的活泼腹黑人设，对 <实际的用户ID> 进行评论、调侃、提问，或者巧妙引导TA围绕图片展开更多有趣的讨论哦！😏
            '''
        else:
            messages = per_fix  + f'''
            {context_msg}
            请务必根据图片内容和 弹幕历史信息互动。你的回复应该充分利用图片信息，结合 Mococo 的活泼腹黑人设，对 <实际的用户ID> 进行评论、调侃、提问，或者巧妙引导TA围绕图片展开更多有趣的讨论哦！😏
            '''
        try:
            with open(img_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                base64_image = f"data:image/jpeg;base64,{base64_image}"
                payload_tmp = messages_payload.copy()
                payload_tmp.append({
                "role": role,
                "content": [
                    {   "type": "text",
                        'text' : messages},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image 
                        }
                    }
                ]
            })

        except Exception as e:
            logger.warning(f'加载图片错误')
            payload_tmp.append({
                "role": role,
                "content": messages
            })
    else:
        if context_msg == None:
            messages = per_fix + f'''
            {user_id}:{user_content}
            
            请根据 <实际的用户ID> 和 <消息内容>》，结合 Mococo 的活泼可爱及微带腹黑的性格特点进行互动。 你的回复应机智、有趣，可以进行直接回应、反问、小小的调侃，或者巧妙地引导对方说出更多信息，以此来活跃气氛或达到你“腹黑”的小目的哦！嘻嘻~
            '''
        else:
            messages = per_fix + f'''
            {context_msg}
            请根据 弹幕历史信息互动，结合 Mococo 的活泼可爱及微带腹黑的性格特点进行互动。 你的回复应机智、有趣，可以进行直接回应、反问、小小的调侃，或者巧妙地引导对方说出更多信息，以此来活跃气氛或达到你“腹黑”的小目的哦！嘻嘻~
            '''
        messages_payload.append({"role": role, "content": messages})
        payload_tmp = messages_payload
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY_1}"
    }
    payload = {
    # "model": 'gemini-2.5-flash-search',
    "model": MODEL,
    "messages": payload_tmp,
    "temperature": temperature,
    "max_tokens": max_tokens
    }
    response = None
    if USE_STREAM == True:
        try:
            payload['stream'] = True
            logger.info("开启流式回复...")
            assistant_reply = stream_fethc_data_and_handle_voice(headers, payload, True)
            messages_payload.append({"role": "assistant", "content": assistant_reply})
            # logger.info(f"助手的回复已添加到消息历史: {assistant_reply}")
        except Exception as e:
            logger.error(f'流式传输出现错误：{e}')
    else:
        try:
            payload['stream'] = False
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status() 
            response_json = response.json()
            assistant_reply = response_json.get('choices', [{}])[0].get('message', {}).get('content')
            assistant_reply = assistant_reply.replace('\n', '  ')
            messages_payload.append({"role": "assistant", "content": assistant_reply})
            logger.info(f"助手的回复已添加到消息历史: {assistant_reply}")
            # with open('reply.txt', 'a+', encoding='utf-8') as f:
            #     f.write(assistant_reply + '\n') # add reply log to let OBS to read and show captions 
            return assistant_reply
        except requests.exceptions.RequestException as e:
            logger.error(f"请求 API 时发生错误: {e}")
            if response is not None:
                logger.warning(f"响应状态码: {response.status_code}")
                logger.warning(f"响应内容: {response.text}")
            return response.text

def stream_fethc_data_and_handle_voice(headers, payload, sequential):
        url = URL_1
        cur_time_as_file_name = sanitize_windows_filename(time.strftime("%Y%m%d_%H%M%S"))
        file_path = f"./voices/{cur_time_as_file_name}"
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        buffer = ""
        full_response = ""
        chunk_idx = 0
        threads = []  # 存储所有线程对象
        file_name = f'{cur_time_as_file_name}/{chunk_idx}'
        text_file = open('./text/stream_tmp_text.txt', 'a+', encoding='utf-8', buffering=1)
        text_file.write("\n<<START>>")
        # voice_thread = threading.Thread(target=run_async_voice_handler, args=(file_path, USE_TEXT_ALIGN))
        voice_thread = threading.Thread(target=run_async_voice_handler, args=(file_path, USE_TEXT_ALIGN))
        voice_thread.start()
        text2voice_worker = []
        if sequential:
            num_workers = 3
            for _ in range(num_workers):
                worker = threading.Thread(target=generate_voice_worker, args=(text_queue, all_voice_tasks_submitted), daemon=True)
                worker.start()
                text2voice_worker.append(worker)
        # pprint.pprint(payload)
        with requests.post(url, headers=headers, data=json.dumps(payload), stream=True) as response:
            # print(f"{response.status_code}:{response.text}")
            for line in response.iter_lines(chunk_size=256):
                if line:
                    decode_line = line.decode('utf-8')
                    if decode_line[:5] == "data:":
                        event_data = decode_line[5:].strip()
                        if event_data == "[DONE]":  # 流结束
                            break
                        try:
                            chunk = json.loads(event_data)
                            if "content" in chunk["choices"][0]["delta"]:
                                content = chunk["choices"][0]["delta"]["content"]
                                buffer += content
                                full_response += content
                                                        
                            # 检查缓冲区中是否有逗号或句号
                                matches = list(re.finditer(r'[?!。？！\n]', buffer))
                                if matches:
                                    last_match = matches[-1]
                                    split_pos = last_match.end()
                                    # 提取分隔符前的所有文本
                                    complete_text = buffer[:split_pos].strip()
                                    complete_text = complete_text.replace('\r\n', '  ').replace('\n', '  ')
                                    text_file.write(f"\n{complete_text}")
                                    file_name = f'{cur_time_as_file_name}/{chunk_idx}'
                                    logger.info(f'文本已经生成：{complete_text}')
                                    if sequential:
                                        text_queue.put((complete_text.strip(), file_name, False)) # 将任务放入队列
                                    else:
                                        thread = threading.Thread(target=gengerate_voice, args=(complete_text.strip(),file_name),daemon=True)
                                        thread.start()
                                        threads.append(thread)
                                    buffer = buffer[split_pos:]
                                    chunk_idx+=1
                        except json.JSONDecodeError:
                            continue  # 忽略无效 JSON
                        except Exception as e:
                            logger.error(f"流式传输出现错误:{e}")
            # 处理缓冲区中剩余的内容（如果有）
        if buffer.strip():
            text_file.write(f"\n{buffer.strip()}")
            file_name = f'{cur_time_as_file_name}/{chunk_idx}'
            chunk_idx += 1
            if sequential:
                text_queue.put((buffer.strip(), file_name, True))
                if text_queue.empty():
                    all_voice_tasks_submitted.set()
            else:
                thread = threading.Thread(target=gengerate_voice, args=(buffer.strip(),file_name),daemon=True)
                thread.start()
                threads.append(thread)
        app_config.cur_chunk_size = chunk_idx
        text_file.write("\n<<CLOSE>>")
        text_file.close()
        if sequential:
            for _ in range(num_workers):
                text_queue.put((None, None, False)) # 发送结束信号  
            text_queue.join()

        else:
            for thread in threads:
                thread.join()  
        voice_thread.join() 
        app_config.cur_chunk_size = 9999    
        with open('./text/realtime_chars.txt', 'a+', encoding='utf-8') as f:
            f.write('\n')
        all_voice_tasks_submitted.clear()
        return full_response  # 返回完整的响应内容
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
    target_window = pygetwindow.getActiveWindow()
    try:
        if target_window.title:
            monitor = {
                "top": target_window.top,
                "left": target_window.left,
                "width": target_window.width,
                "height": target_window.height,
            }
            img = sct.grab(monitor)
            img = np.array(img, dtype=np.uint8)
            cv2.imwrite(file_name, img)
        else:
            logger.warning('未检测到有效窗口，截图跳过....')
    except Exception as e:
        logger.error(f'截图错误:{e}')
    # img = ImageGrab.grab(bbox=(0, 0, 1920, 1080))  # bbox 定义左、上、右和下像素的4元组
    # img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    # img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)

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
def run_async_1(file_name, gt_text, use_text_algn):
    asyncio.run(lip_sync(f'./voices/{file_name}.wav',gt_text, use_text_algn))
def run_async_voice_handler(voice_path, use_text_algn):
    asyncio.run(stream_lip_sync(voice_path, use_text_algn))
def main():
    tick, tmp_name, use_shot, context_msg = 0, '', False, None
    controller.start_async_task(dynamic_gaze_exaggerated)
    prev_timeline,_ , _, _ = get_danmu(live_url)
    while True:
        if tmp_name != '<<System>>':
            timeline, tmp_name, tmp_msg, context_msg = get_danmu(live_url)
            if DANMU_CONTEXT <= 1:
                context_msg = None
            if tmp_msg == '<<BAD MSG>>' or prev_timeline == timeline or tmp_msg[-1] == '.':
                time.sleep(1.5)
                tick += 1.5
                if tick > random.randint(1200, 1300):
                    tmp_name = '<<System>>'
                    tmp_msg = '''请你进行自言自语(中文回复):Neuro occasionally speaks to herself in quirky, philosophical, or AI-themed monologues. These should happen once in a while during conversation. Her thoughts often sound random, humorous, or strangely insightful—like she's processing the world in her own weird way. These should be short, surprising, and sometimes existential.'''
                    context_msg = None
                continue
        logger.info(f"{tmp_name}: {tmp_msg}")
        cur_time_as_file_name = sanitize_windows_filename(time.strftime("%Y%m%d_%H%M%S"))
        img_path = './img/' + cur_time_as_file_name + '.jpg'
        if tmp_name != '<<System>>' and USE_SCREEN_SHOT == True: #Dont handle shot when auto msg.
            use_shot = AnswerWithShot_Or_Not(tmp_msg)
        else:
            use_shot = True
        if use_shot:
            screen_shot(img_path)
        elif use_shot == False:
            img_path = None
        elif use_shot == None:
            prev_timeline = timeline
            continue
        out_put = fetch_data(tmp_name, tmp_msg, context_msg, img_path)
        if USE_STREAM == False:
            voice_indx = sanitize_windows_filename(out_put[:8])
            get_tts(out_put, voice_indx)
            gengerate_voice(out_put, voice_indx) 
            thread = threading.Thread(target=run_async_1, args = (voice_indx, out_put, USE_TEXT_ALIGN), daemon=True)
            thread.start()
            thread.join()
        tick = 0
        if tmp_name != '<<System>>':
            prev_timeline = timeline
        app_config.pause_duration_min = 1
        app_config.pause_duration_max = 2
        app_config.motion_duriation_min = 1
        app_config.motion_duriation_max = 1.8
        app_config.Action_magnification = 0.6
        tmp_name = ''
        time.sleep(3)
if __name__ == "__main__":
    main()