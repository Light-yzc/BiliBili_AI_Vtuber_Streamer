import asyncio
import json
import threading
import numpy as np
import librosa
import sounddevice as sd
from websockets import connect
from playsound import playsound
from config import app_config
from text_align import *
import time

with open('./config.json', 'r', encoding='utf-8') as file:
    GLOBAL_CONFIG = json.load(file)
    WS_URI= GLOBAL_CONFIG['ws_host']
    if GLOBAL_CONFIG['use_text_align']:
        model_a, metadata, device = load_whisper_model()

is_play = 0

# 共享数据结构
class AudioState:
    def __init__(self):
        self.audio_data = None
        self.sample_rate = 44100
        self.frame_size = int(44100 / 10)  # 30fps
        self.position = 0
        self.amplitude = 0.0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
    def reset(self):
        with self.lock:
            self.position = 0
            self.amplitude = 0.0
            self.stop_event.clear()
# 全局状态实例
audio_state = AudioState()

def audio_play_thread(mp3_path, aligned_data_list, output_file_path="./text/realtime_chars.txt"):
    """
    独立音频播放线程，并在播放中实时将字符写入文件。

    Args:
        mp3_path (str): 音频文件路径。
        aligned_data_list (list): WhisperX 对齐结果中的 'chars' 或 'words' 列表，
                                   例如 aligned_result['segments'][0]['chars']。
        output_file_path (str): 实时写入字符的目标文件路径。
    """
    # 加载音频
    audio, sr = librosa.load(mp3_path, sr=audio_state.sample_rate, mono=True)
    audio = np.clip(audio * 3, -1.0, 1.0) # 振幅调整

    # 初始化音频设备
    stream = sd.OutputStream(
        samplerate=audio_state.sample_rate,
        channels=1,
        dtype='float32',
        blocksize=audio_state.frame_size, # 使用frame_size作为blocksize
        latency='low'
    )
    if aligned_data_list != None:
        # 初始化用于实时写入的变量
        current_char_index = 0
        # 打开文件用于写入，'w' 模式会清空文件，'a' 模式会追加
        # 这里我们用 'w' 确保每次播放都是新的写入
        output_file = open(output_file_path, 'a+', encoding='utf-8') 
        output_file.write('\n')
        with stream:
            audio_state.audio_data = audio
            print(f"开始播放音频，并将字符实时写入：{output_file_path}")
            
            while not audio_state.stop_event.is_set():
                # 获取当前播放的样本位置
                with audio_state.lock:
                    start_sample = audio_state.position
                    
                    # 计算当前播放时间（秒）
                    current_play_time_sec = start_sample / audio_state.sample_rate

                    end_sample = start_sample + audio_state.frame_size
                    if start_sample >= len(audio_state.audio_data):
                        break # 音频播放完毕

                    chunk = audio_state.audio_data[start_sample:end_sample]
                    audio_state.position = end_sample # 更新音频播放位置
                    
                # --- 实时字符写入逻辑 ---
                # 遍历对齐数据，将到达播放时间的字符写入文件
                while current_char_index < len(aligned_data_list):
                    char_info = aligned_data_list[current_char_index]
                    char = char_info['word']
                    char_start_time = char_info['start']
                    
                    # 如果当前播放时间已经超过或等于字符的开始时间，就写入
                    if current_play_time_sec >= char_start_time:
                        output_file.write(char)
                        output_file.flush() # 立即写入文件，而不是等待缓冲区满
                        # print(f"写入字符: '{char}' at {current_play_time_sec:.3f}s") # 调试用
                        current_char_index += 1 # 移动到下一个字符
                    else:
                        break # 还没有到下一个字符的播放时间，跳出内层循环
                # --- 实时字符写入逻辑结束 ---
                # 计算振幅（线程安全）
                amp = np.sqrt(np.mean(chunk**2)) * 6
                with audio_state.lock:
                    audio_state.amplitude = np.clip(amp, 0, 1).astype(float)
                
                # 播放音频
                stream.write(chunk.astype('float32'))
                
                # 精确睡眠保持每秒处理30帧（如果blocksize是sr/30的话）
                # 注意：实际播放时间由 stream.write() 和 blocksize 决定，sd.sleep 主要是为了降低CPU占用
                # 这里的 sd.sleep(int(1000 / 30)) 会导致播放速度变慢，因为每次循环会额外等待
                # 更准确的做法是根据实际处理的音频块大小来调整，或者移除 sd.sleep
                # 如果你的blocksize已经确保了播放速度，可以移除 sd.sleep
                # 或者将其调整为更小的等待，比如 stream.write() 后通常是阻塞的，无需额外睡眠
                # sd.sleep(int(audio_state.frame_size / audio_state.sample_rate * 1000)) # 睡眠对应音频块的时长
            output_file.write(aligned_data_list[-1]['word'])
            print("音频播放完毕或停止事件触发。")
            output_file.close() # 关闭文件
    else:
        with stream:
            audio_state.audio_data = audio
            while not audio_state.stop_event.is_set():
                with audio_state.lock:
                    start = audio_state.position
                    end = start + audio_state.frame_size
                    if start >= len(audio_state.audio_data):
                        break
                    chunk = audio_state.audio_data[start:end]
                    audio_state.position = end
                    
                # 计算振幅（线程安全）
                amp = np.sqrt(np.mean(chunk**2)) * 6
                with audio_state.lock:
                    audio_state.amplitude = np.clip(amp, 0, 1).astype(float)
                
                # 播放音频
                stream.write(chunk.astype('float32'))
                # 精确睡眠保持30fps
                sd.sleep(int(1000 / 30))  
    print("播放线程结束。")

async def lip_sync(mp3_path, gt_text, use_text_algn = False):
    with open(r'./config.json', 'r', encoding='utf-8') as file:
        GLOBAL_CONFIG = json.load(file)
    if use_text_algn == False:
        with open('./text/realtime_chars.txt', 'a+', encoding='utf-8') as f:
            f.write('\n' + gt_text) # add reply log to let OBS to read and show captions 
    global is_play  
    audio_state.reset()
    """主异步函数处理VTS通信"""
    AUTH_TOKEN = GLOBAL_CONFIG['vts_authenticationToken']
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
        print("认证响应:", json.loads(auth_response))
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


# if __name__ == "__main__":
#     asyncio.run(lip_sync(r"E:\Code\AI_Vtuber_by_tavern\voices\test_align.mp3", "一起玩吗？莫可可超想的啦。嗯，可是你看，master现在在弄那个服务器哟，okay？好像出了点问题，所以现在还不能玩啦。"))