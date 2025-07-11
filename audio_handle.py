import asyncio
import json
import threading
import numpy as np
import librosa
import sounddevice as sd
from websockets import connect
from playsound import playsound
from config import DEFAULT_CONFIG
is_play = 0
WS_URI = "ws://localhost:8088"

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

def audio_play_thread(mp3_path):
    """独立音频播放线程"""
    # 加载音频
    audio, sr = librosa.load(mp3_path, sr=audio_state.sample_rate, mono=True)
    
    # 初始化音频设备
    stream = sd.OutputStream(
        samplerate=audio_state.sample_rate,
        channels=1,
        dtype='float32',
        # blocksize=audio_state.frame_size,
        blocksize=8024,
        latency='low'
    )
    
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

async def lip_sync(mp3_path):
    with open(r'./config.json', 'r', encoding='utf-8') as file:
        GLOBAL_CONFIG = json.load(file)
    global is_play  
    audio_state.reset()
    """主异步函数处理VTS通信"""
    AUTH_TOKEN = GLOBAL_CONFIG['vts_authenticationToken']
    
    # 启动音频线程
    audio_thread = threading.Thread(
        target=audio_play_thread,
        args=(mp3_path,),
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
        DEFAULT_CONFIG['statue'] = 2
        while audio_thread.is_alive():

            # 获取当前振幅（线程安全）
            with audio_state.lock:
                mouth_open = audio_state.amplitude
            
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
    DEFAULT_CONFIG['statue'] = 1


# async def main():
#     await lip_sync(r"D:\Code\vtuber\voices\1.mp3")  # 替换为实际路径

# if __name__ == "__main__":
#     asyncio.run(main())