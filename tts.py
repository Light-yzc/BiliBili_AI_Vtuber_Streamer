import requests
import wave
import json
import os
from audio_handle import audio_state
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from config import app_config
logger = app_config.logger
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
    file_path = f'./voices/{file_name}.wav' 

    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"文件 {file_path} 已删除")
    else:
        logger.info(f"文件 {file_path} 已生成")

    with open(file_path, 'wb') as f:
        f.write(data)
def get_tts(txt, file_name):
    with open('./config.json', 'r', encoding='utf-8') as file:
        config= json.load(file)
        api = config['api-key-tts']
        url = config['api-url-tts']
    payload = {
        "input": txt,
        "response_format": "wav",
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
    bin_to_mp3(response.content, file_name)
    logger.info(str(response)+'已经执行生成语音指令')
# BY local TTS
def gengerate_voice(text, file_name):
    global tmp_file,i,ref_path
    max_retries = 2
    
    ref_path = os.path.dirname(os.path.abspath(__file__)) + '/gpt_sovits_ref/ref.wav'
    corrected_file_path = ref_path.replace('\\', '/')
    url = f'http://127.0.0.1:9880/?refer_wav_path='+ corrected_file_path + '&prompt_text=やめない、壊れそうだから、さきが壊れたら&prompt_language=ja&text=' + text + '&text_language=zh&top_k=15&top_p=1&temperature=1&speed=0.8&cut_punc=，。`'
    #NEW model url
    # ref_path = 'D:/gpt_sovits_ref/ref.wav'
    # url = f'http://127.0.0.1:9880/?refer_wav_path='+ ref_path + '&prompt_text=やめない、壊れそうだから、さきが壊れたら&prompt_language=ja&text=' + text + '&text_language=zh&top_k=5&top_p=0.6&temperature=1&speed=0.8&cut_punc=，。`'

    retry_strategy = Retry(total=max_retries, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=['GET'])
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    try:
        logger.info(f'开始获取语音：{file_name}')
        response = session.get(url=url, timeout=(5, 10))
        response.raise_for_status()  # 检查HTTP状态码（4xx/5xx会抛异常）
        bin_to_mp3(response.content, file_name)
    except Exception as e:
        logger.error(e)
        logger.warning("------tts的Api服务器不可用，跳过声音生成------")

# test_text = '''你好啊，我是mococo'''
# gengerate_voice(test_text,'./test2')

