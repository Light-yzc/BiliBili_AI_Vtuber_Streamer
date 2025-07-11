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
def bin_to_mp3(data, file_name):
    file_path = f'./voices/{file_name}.mp3'  # 替换为你的文件路径

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"文件 {file_path} 已删除")
    else:
        print(f"文件 {file_path} 不存在")

    with open(file_path, 'wb') as f:
        f.write(data)
def get_tts(txt, file_name):
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
    bin_to_mp3(response.content, file_name)
    print(str(response)+'已经执行生成语音指令')
# BY local TTS
def gengerate_voice(text, file_name):
    global tmp_file,i,ref_path
    ref_path = os.path.dirname(os.path.abspath(__file__)) + '/ref.wav'
    corrected_file_path = ref_path.replace('\\', '/')
    url = f'http://127.0.0.1:9880/?refer_wav_path='+ corrected_file_path + '&prompt_text=やめない、壊れそうだから、さきが壊れたら&prompt_language=ja&text=' + text + '&text_language=zh&top_k=15&top_p=1&temperature=1&speed=0.8&cut_punc=。`'
    try:
        response = requests.get(url=url)
        bin_to_mp3(response.content, file_name)
    except:
        print("------tts的Api服务器不可用，跳过声音生成------")

