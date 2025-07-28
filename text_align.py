import whisperx
import gc
import torch
import os
from audio_handle import *
from config import app_config
#这个文件还在测试，主要是为了实现类似于音频读出一个字文本就输出一个字
#但是目前还在测试，基本功能可以运行，可在config.json中use_text_align=true开启

# whisper_model_name = "TencentGameMate/chinese-wav2vec2-base" # 这里的Whisper模型不会用于识别，只是load_align_model需要一个base name
logger = app_config.logger
def load_whisper_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16"

    try:
        # 这里的 whisper_model_name 只是用来告诉 load_align_model 需要哪个语言的对齐模型，
        # 实际上并不会加载完整的Whisper转录模型。
        model_a, metadata = whisperx.load_align_model(
            # model_name = whisper_model_name,
            language_code="zh",
            device=device,
        )
        logger.info("对齐模型加载成功。")
    except Exception as e:
        logger.error(f"加载对齐模型失败：{e}")
        logger.error("请确保网络连接正常，并且 'model_name' 和 'language_code' 正确。")
        logger.error("如果仍有问题，尝试手动下载模型文件到缓存目录。")
        exit()
    return model_a, metadata, device

def clear_gpu_memory(device):
    if device == "cuda":
        torch.cuda.empty_cache()
        gc.collect()

def text_algn(model_a, metadata, device, audio_path, gt_text):
    audio_file_path = audio_path  # 替换为你的生成语音文件路径
    ground_truth_text = gt_text # 替换为你的完整原始文本
    if not os.path.exists(audio_file_path):
        logger.error(f"错误：音频文件未找到在 {audio_file_path}")
        logger.error("请将 'audio_file_path' 变量替换为你的实际音频文件路径。")
        exit()
    logger.info(f"正在加载音频文件: {audio_file_path} 并进行VAD...")
    audio = whisperx.load_audio(audio_file_path)

    audio_duration = len(audio) / 16000.0 # 计算音频时长 (16000是whisperx默认采样率)
    segments = [
        {"text": ground_truth_text, "start": 0.0, "end": audio_duration}
    ]

    logger.info(f"准备对齐文本: '{ground_truth_text}' (总时长: {audio_duration:.2f} 秒)")
    logger.info("正在加载中文对齐模型 (基于 Wav2Vec2 + CTC)...")
    logger.info("正在执行强制对齐...")
    try:
        with torch.no_grad():
            aligned_result = whisperx.align(
                transcript=segments,
                model=model_a,
                align_model_metadata=metadata,
                audio=audio,
                device=device,
                return_char_alignments=True
            )
        logger.info("强制对齐完成。")
    except Exception as e:
        logger.error(f"执行对齐失败：{e}")
        logger.error("请检查输入音频和文本是否匹配。")
        exit()
    # 防止显存泄露
    # 1. 删除不再需要的大变量
    del audio
    del segments
    
    # 2. 清除PyTorch缓存
    if device == "cuda":
        torch.cuda.empty_cache()
    
    # 3. 手动触发垃圾回收
    gc.collect()
    logger.info("\n--- 对齐成功 ---")
    return audio_path, aligned_result


    # for segment in aligned_result["segments"]:
    #     audio_thread = threading.Thread(target=audio_play_thread,
    #                                     args=(audio_file_path, segment["words"]),
    #                                     daemon=True)
    #     audio_thread.start()
    # audio_thread.join()
    #     print(f"处理段落文本: \"{segment['text']}\"")
    #     # 如果 return_char_alignments=True，结果会在 'chars' 中
    #     # 否则在 'words' 中，这里我们同时遍历
        
    #     if 'words' in segment:
    #         print("  --- 词语级别时间戳 ---")
    #         for word_info in segment["words"]:
    #             word = word_info['word']
    #             start = word_info['start']
    #             end = word_info['end']
    #             score = word_info.get('score', 'N/A') # 对齐置信度
    #             print(f"    词语: '{word}' | 开始: {start:.3f}s | 结束: {end:.3f}s | 置信度: {score:.4f}")

    # if 'chars' in segment:
    #     print("  --- 字符级别时间戳 ---")
    #     for char_info in segment["chars"]:
    #         char = char_info['char']
    #         start = char_info['start']
    #         end = char_info['end']
    #         score = char_info.get('score', 'N/A')
    #         print(f"    字符: '{char}' | 开始: {start:.3f}s | 结束: {end:.3f}s | 置信度: {score:.4f}")
