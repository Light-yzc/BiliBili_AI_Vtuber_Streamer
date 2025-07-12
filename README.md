# Bilibili AI 直播主播 Demo  


> 基于 B 站直播接口 + LLM + TTS 的 AI 主播演示项目，支持本地化部署与自定义角色设定  

---

## 📌 项目简介  
本项目是一个基于 B 站直播平台的 AI 主播演示系统，通过集成大语言模型（LLM）和语音合成（TTS）技术，实现实时弹幕交互、角色扮演和语音播报功能。支持主流 LLM API（如 OpenAI、DeepSeek）和本地化部署（如 GPT-SoVITS 模型），无需依赖第三方框架（如酒馆系统）。  

---

## ✨ 功能特性  
- **实时弹幕处理**：自动抓取 B 站直播间弹幕并解析用户输入  
- **多模型支持**：兼容 OpenAI、DeepSeek 等主流 LLM API，支持自定义本地模型  
- **模块化 TTS 架构**：兼容GPT-SoVITS 本地语音合成模型，或调用在线 TTS 服务  
- **角色自定义**：通过 Prompt 配置实现个性化主播角色（如虚拟偶像、知识问答等）  
- **无依赖部署**：无需依赖酒馆系统，直接对接 B 站直播接口  
- **📸 智能截图辅助**：动态判断是否截取当前直播画面辅助 AI 决策（截图存储于 ./img 目录）
---

## 🧠 技术架构  
```
B 站直播接口 ←(弹幕输入)→ AI 主播系统 →(语音输出)→ VTS/VirtualYou  
                    ↑(LLM 调用1)小模型验证   ↑(TTS 调用)  
                    └─ OpenAI/DeepSeek      └─ GPT-SoVITS/在线 TTS  
                    ↑（LLM 调用2）大模型输出
                    └─ OpenAI/DeepSeek
```                                 

---

## 🛠️ 安装与配置  

### 1. 依赖项安装  
```bash  
pip install -r requirements.txt  
# 若使用 GPT-SoVITS 本地模型，请额外安装对应依赖  
```

### 2. 配置文件说明  
修改 `config.json` 文件以适配您的环境：  
```json  
{  
  "status": 1,  
  "msg_filter": ["互关", "关注", "回关"],  // 过滤敏感关键词  
  "api_key_tts": "your-tts-api-key",     // TTS 服务 API 密钥（如 SiliconFlow）  
  "api_url_tts": "https://api.siliconflow.cn/v1/audio/speech",  // TTS 请求地址  
  "api_key_llm_1": "your-llm-api-key-1", // 主 LLM API 密钥（用于主播回复）  
  "api_key_llm_2": "your-llm-api-key-2", // 次 LLM API 密钥（用于过滤无意义消息和是否截取当前屏幕进行辅助AI回复）  
  "api_url_1": "https://api.openai.com/v1/chat/completions",    // 主 LLM 请求地址  
  "api_url_2": "https://api.deepseek.com/v1/chat/completions",  // 次 LLM 请求地址  
  "live_url": "https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid=YOUR_ROOM_ID&room_type=0",  //更改YOUR_ROOM_ID为你的直播间地址
  "ws_host":"ws://localhost:8088",  //vtuber studio websocket地址
  "vts_authenticationToken": ""  // VTS 认证令牌 （可以不填，留空第一次自动获取）
}  
```

---

## ▶️ 使用说明  

### 1. 启动服务  
```bash  
python main.py  
```

### 2. 关键配置步骤  
1. **修改直播间地址**  
   在 `main.py` 中替换您的直播间地址：  
   ```python
   live_url = "https://live.bilibili.com/your_room_id"  # 替换为你的直播间地址
   ```

2. **配置 TTS 模式**  
   - 使用在线 API：确保 `config.json` 中填写有效的 TTS API 地址和密钥  
   - 使用本地模型：部署 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 并修改代码中的调用逻辑  

3. **角色设定**  
   在 `main.py` 中的`Prompt`中自定义主播角色设定，例如：  
   ```text
   你是一个活泼的虚拟偶像，用元气满满的日语和观众互动！
   ```

---

## 📺 效果展示  
- **演示视频**：[B站直播演示](https://www.bilibili.com/video/BV1EDLhzCE9x/)  
- **界面截图**：  
  ![屏幕截图](https://github.com/user-attachments/assets/a600c6cb-0ad0-46a1-8f48-1c59c486c0b2)

---

## 🧪 版本更新日志  
### Version 0.1 (2025-07-11)  
- 更改 API 调用方式，不再依赖酒馆系统  
- 新增本地 TTS 支持（GPT-SoVITS）  
- 实现 TTS 响应持久化存储  
- 优化弹幕过滤逻辑  
### Version 0.1.1 (2025-07-12)  
- 增加截屏功能，和小模型联合判断回复是否需要截屏操作
---

## 📜 许可证  
本项目采用 [MIT License](https://github.com/yourusername/bilibili-ai-live-demo/blob/main/LICENSE)，可自由商用和修改，但需保留原作者信息。