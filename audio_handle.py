import asyncio
import json
import threading
import numpy as np
import librosa
import sounddevice as sd
from websockets import connect
from playsound import playsound
from config import app_config
import time
import os
with open('./config.json', 'r', encoding='utf-8') as file:
    GLOBAL_CONFIG = json.load(file)
    WS_URI = GLOBAL_CONFIG['ws_host']
    AUTH_TOKEN = GLOBAL_CONFIG['vts_authenticationToken']

    if GLOBAL_CONFIG['use_text_align']:
        from text_align import *
        model_a, metadata, device = load_whisper_model()
    else:
        model_a, metadata, device = None, None, None
logger = app_config.logger
is_play = 0

class AudioState:
    def __init__(self):
        self.audio_data = None
        self.sample_rate = 44100
        # self.frame_size = int(44100 / 10) # 原始是30fps, 10应该是笔误，改为30
        self.frame_size = int(44100 / 30) # 30fps
        self.position = 0
        self.amplitude = 0.0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self._stream = None # 私有变量，用于存储预初始化的音频流

    def reset(self):
        with self.lock:
            self.position = 0
            self.amplitude = 0.0
            self.stop_event.clear()
            # 如果流正在运行，停止它以准备下一次播放
            if self._stream:
                self._stream.stop()

    def get_stream(self):
        # 懒加载或确保流已初始化
        if self._stream is None or not self._stream.closed: # 检查流是否已关闭
            try:
                self._stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32',
                    blocksize=self.frame_size,
                    latency='low'
                )
            except Exception as e:
                logger.error(f"初始化音频流失败: {e}")
                self._stream = None # 如果失败，将其设为None
        return self._stream

# 全局状态实例
audio_state = AudioState()

# (可选) 在程序启动时尝试获取并初始化流一次
stream_on_startup = audio_state.get_stream()
if stream_on_startup:
    logger.info("音频流已预初始化。")
else:
    logger.warning("音频流预初始化失败，将按需初始化。")


def audio_play_thread(mp3_path, aligned_data_list, output_file_path="./text/realtime_chars.txt"):
    """
    独立音频播放线程，并在播放中实时将字符写入文件。
    """
    # 加载音频
    try:
        audio, sr = librosa.load(mp3_path, sr=audio_state.sample_rate, mono=True)
        audio = np.clip(audio * 2.5, -1.0, 1.0) # 振幅调整
    except:
        logger.error('音频播放失败')
    # 获取音频流实例
    stream = audio_state.get_stream()
    if stream is None:
        logger.error("错误：无法获取或初始化音频流，无法播放。")
        return

    # 在播放前确保流已停止并准备好
    if stream.closed: # 如果流在某个时刻被外部关闭了，重新获取
        stream = audio_state.get_stream()
        if stream is None:
            logger.error("错误：重新初始化音频流失败，无法播放。")
            return

    # 开始音频流
    try:
        stream.start()
    except sd.PortAudioError as e:
        logger.error(f"启动音频流失败: {e}")
        return

    # 文件写入逻辑 (保持不变)
    output_file = None
    if aligned_data_list is not None:
        current_char_index = 0
        output_file = open(output_file_path, 'a+', encoding='utf-8')
        output_file.write('\n')
        logger.info(f"开始播放音频，并将字符实时写入：{output_file_path}")

    audio_state.audio_data = audio # 将音频数据设置到共享状态

    try:
        while not audio_state.stop_event.is_set():
            with audio_state.lock:
                start_sample = audio_state.position
                current_play_time_sec = start_sample / audio_state.sample_rate
                end_sample = start_sample + audio_state.frame_size

                if start_sample >= len(audio_state.audio_data):
                    break # 音频播放完毕

                chunk = audio_state.audio_data[start_sample:end_sample]
                audio_state.position = end_sample # 更新音频播放位置

            # --- 实时字符写入逻辑 ---
            if aligned_data_list is not None and output_file is not None:
                while current_char_index < len(aligned_data_list):
                    char_info = aligned_data_list[current_char_index]
                    char = char_info['word']
                    char_start_time = char_info['start']

                    if current_play_time_sec >= char_start_time:
                        output_file.write(char)
                        output_file.flush()
                        current_char_index += 1
                    else:
                        break
            # --- 实时字符写入逻辑结束 ---

            amp = np.sqrt(np.mean(chunk**2)) * 6
            with audio_state.lock:
                audio_state.amplitude = np.clip(amp, 0, 1).astype(float)

            stream.write(chunk.astype('float32'))

            # 精确睡眠的移除或调整，取决于你的 `blocksize` 是否足够维持实时性
            # 如果 `stream.write()` 是阻塞的，通常不需要额外的 `sd.sleep`
            # 如果需要，可以考虑 `sd.sleep(int(audio_state.frame_size / audio_state.sample_rate * 1000))`
            # 或者移除此行，让 stream.write() 控制节奏。
            # sd.sleep(int(1000 / 30))

    except Exception as e:
        logger.error(f"播放过程中发生错误: {e}")
    finally:
        # 播放结束后停止流
        stream.stop()
        if aligned_data_list is not None and output_file is not None:
            output_file.write('\n' + aligned_data_list[-1]['word']) # 确保最后一个词也被写入
            output_file.close() # 关闭文件
        logger.info("音频播放完毕或停止事件触发。")

async def lip_sync(mp3_path, gt_text, use_text_algn = False):
    if use_text_algn == False and gt_text != None:
        with open('./text/realtime_chars.txt', 'a+', encoding='utf-8') as f:
            f.write('\n' + gt_text) # add reply log to let OBS to read and show captions 
    global is_play  
    audio_state.reset()
    """主异步函数处理VTS通信"""
    aligned_words_for_play = None
    audio_file_to_play = mp3_path
    if use_text_algn == True:
        alignment_start_time = time.time()
        audio_file_to_play, aligned_data = await asyncio.to_thread(
            text_algn, model_a, metadata, device, mp3_path, gt_text, )
        alignment_end_time = time.time()
        print(f"语音对齐完成，耗时: {alignment_end_time - alignment_start_time:.2f} 秒。")
        if audio_file_to_play is None or aligned_data is None:
            print("对齐失败，无法继续播放。")
            return # 对齐失败，直接退出 ##照理来说可以直接播放，逻辑以后再优化吧
        
        if aligned_data and aligned_data['segments'] and 'words' in aligned_data['segments'][0]:
            aligned_words_for_play = aligned_data['segments'][0]['words']
        else:
            print("对齐结果中未找到词语数据。")
            return # 无法继续
    app_config.pause_duration_min = 0.4
    app_config.pause_duration_max = 0.8
    app_config.motion_duriation_min = 0.4
    app_config.motion_duriation_max = 1
    app_config.Action_magnification = 1.2
    # 启动音频线程
    audio_thread = threading.Thread(
        target=audio_play_thread,
        args=(audio_file_to_play, aligned_words_for_play, "./text/realtime_chars.txt"),
        daemon=True
    )

    audio_thread.start()


    async with connect(WS_URI) as websocket:
        # 认证流程
        await websocket.send(json.dumps({
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "123",
        "messageType": "AuthenticationRequest",
        "data": {
            "pluginName": "My Cool Plugin",
            "pluginDeveloper": "My Name",
            "authenticationToken": AUTH_TOKEN
        }
        }))
        auth_response = await websocket.recv()
        # print("认证响应:", json.loads(auth_response))
        app_config.mouth = 2
        while audio_thread.is_alive():

            # 获取当前振幅（线程安全）
            with audio_state.lock:
                mouth_open = audio_state.amplitude
            # print(mouth_open)
            # 发送口型参数
            await websocket.send(json.dumps({
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "MouthControl",
                "messageType": "InjectParameterDataRequest",
                "data": {
                    "faceFound": True,
                    "mode": "set",
                    "parameterValues": [
                        {"id": "MouthOpen", "value": mouth_open*0.5},
                        # {"id": "MouthForm", "value": mouth_open * 0.8}
                    ]
                }
            }))
            
            # 精确同步（30fps）
            await asyncio.sleep(1/30 - 0.001)  # 补偿网络延迟

            response = await websocket.recv()
            # print("口型:", json.loads(response))
            
    audio_state.stop_event.set()
    audio_thread.join()
    app_config.mouth = 1

async def stream_lip_sync(voice_path, use_text_algn = False):
    text_file = open('./text/stream_tmp_text.txt', 'r', encoding='utf-8')
    last_start_content = [] # 用于存储最后一个 <<START>> 之后的内容
    found_start = False     # 标记是否已经找到了至少一个 <<START>>
    cur_index = 0
    Last_text = ''
    start = time.time()
    while True:
        if len(last_start_content) != 0:
            Last_text = last_start_content[-1]
        if '<<CLOSE>>' not in Last_text:
            for line in text_file:
                if '<<START>>' in line:
                    # 每次找到 <<START>>，就清空之前的所有内容
                    # 并从当前行的 <<START>> 之后开始记录
                    last_start_content = []
                    found_start = True
                    line_part = line.split('<<START>>')[-1] # 获取 <<START>> 之后的部分
                    if line_part.strip() and line_part != '\n':
                        last_start_content.append(line_part)
                elif found_start:
                    # 如果已经找到了 <<START>>，就将后续所有行都添加到列表中
                    stripped_line = line.strip()
                    if stripped_line: # 检查去除空白后是否还有内容
                        last_start_content.append(stripped_line)
            time.sleep(0.2)
        else:
            if cur_index <= len(last_start_content):
                file_path = voice_path + f'/{cur_index}.wav'
                if cur_index+1 == app_config.cur_chunk_size:
                    logger.info('所有语音已经播放完毕')
                    return '<<DONE>>'
                if not os.path.exists(file_path):
                    cur_time = time.time()
                    if cur_time - start > 85:
                        logger.warning('语音获取时间超时，开始退出...')
                        return False
                    time.sleep(0.2)
                else:
                    start = time.time()
                    logger.info(f'开始播放第{cur_index}段音频')
                    logger.info(last_start_content[cur_index])
                    await lip_sync(file_path, last_start_content[cur_index], use_text_algn)
                    cur_index += 1
            else:
                logger.info('所有语音已经播放完毕')
                return '<<DONE>>'
        
# if __name__ == "__main__":
#     asyncio.run(lip_sync(r"E:\Code\AI_Vtuber_by_tavern\voices\test_align.mp3", "一起玩吗？莫可可超想的啦。嗯，可是你看，master现在在弄那个服务器哟，okay？好像出了点问题，所以现在还不能玩啦。"))