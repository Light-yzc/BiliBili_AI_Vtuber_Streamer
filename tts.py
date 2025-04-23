import requests
import wave
import json
import os



def binary_to_wav(data, output_file, sample_rate=44100, channels=1, sample_width=2):
    # 读取二进制文件
    raw_data = data
    
    # 创建WAV文件
    with wave.open(output_file, 'wb') as wav_file:
        wav_file.setnchannels(channels)  # 声道数
        wav_file.setsampwidth(sample_width)  # 采样宽度(字节)
        wav_file.setframerate(sample_rate)  # 采样率
        wav_file.writeframes(raw_data)
def bin_to_mp3(data):
    file_path = './voices/1.mp3'  # 替换为你的文件路径

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"文件 {file_path} 已删除")
    else:
        print(f"文件 {file_path} 不存在")

    with open('./voices/1.mp3', 'wb') as f:
        f.write(data)
def get_tts(txt):
    with open('./config.json', 'r') as file:
        api = json.load(file)['api-key']
    url = "https://api.siliconflow.cn/v1/audio/speech"

    payload = {
        "input": txt,
        "response_format": "mp3",
        "stream": False,
        "speed": 1,
        "gain": 0,
        "model": "FunAudioLLM/CosyVoice2-0.5B",
        "voice": "FunAudioLLM/CosyVoice2-0.5B:diana",
        "sample_rate": 44100
    }
    headers = {
        "Authorization": "Bearer " + str(api),
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    # binary_to_wav(response.content , './1.wav', )
    bin_to_mp3(response.content)
    print(str(response)+'已经执行生成语音指令')

get_tts('你好')