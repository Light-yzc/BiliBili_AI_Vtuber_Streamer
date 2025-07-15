# Bilibili AI 直播主播 Demo

**基于 B 站直播接口、大语言模型 (LLM) 和语音合成 (TTS) 的 AI 主播演示项目，支持本地化部署与自定义角色设定。**

-----

## 📌 项目简介

本项目旨在构建一个功能强大的 B 站 AI 主播演示系统。通过无缝集成大语言模型（LLM）和语音合成（TTS）技术，它能够实现实时的弹幕交互、灵活的角色扮演以及逼真的语音播报。该系统支持主流 LLM API（如 OpenAI、DeepSeek）和本地化部署方案（如 GPT-SoVITS 模型），并且无需依赖第三方框架（如酒馆系统），大大简化了部署流程。

-----

## ✨ 核心功能

  * **实时弹幕互动**：自动抓取 B 站直播间弹幕，智能解析用户输入，实现即时、流畅的互动体验。
  * **多 LLM 模型支持**：灵活兼容 OpenAI、DeepSeek 等主流 LLM API，同时支持集成自定义的本地大语言模型，满足不同需求。
  * **模块化 TTS 架构**：无缝集成 GPT-SoVITS 本地语音合成模型，或选择调用在线 TTS 服务，提供多样化的语音输出选项。
  * **高度可定制角色**：通过简洁的 Prompt 配置，轻松实现个性化的主播角色设定（例如：元气虚拟偶像、专业知识问答助手等）。
  * **轻量级无依赖部署**：直接对接 B 站直播接口，无需额外安装酒馆系统等第三方框架，部署更便捷。
  * **📸 智能截图辅助**：动态判断直播画面内容，在需要时自动截取当前屏幕，为 AI 决策提供视觉辅助（截图文件存储于 `./img` 目录）。

-----

## 🧠 技术架构概览

```
B 站直播接口 ←(弹幕输入)→ AI 主播系统 →(语音输出)→ VTS/VirtualYou  
                    ↑(LLM 调用1) 小模型验证   ↑(TTS 调用)  
                    └─ OpenAI/DeepSeek      └─ GPT-SoVITS/在线 TTS  
                    ↑（LLM 调用2） 大模型输出
                    └─ OpenAI/DeepSeek
```

-----

## 🛠️ 安装与配置指南

### 1\. 依赖项安装

首先，请安装项目所需的 Python 依赖：

```bash
pip install -r requirements.txt
# 如果计划使用 GPT-SoVITS 本地模型，请根据其官方文档额外安装相应的依赖。
```

### 2\. 配置文件说明

请根据您的环境修改 `config.json` 文件：

```json
{
  "statue": 1,
  "msg_filte": ["互关", "关注", "回关", "", " ", "\n"], // 用于过滤直播弹幕中的敏感或无意义关键词
  "api-key-tts": "sk-",  // TTS 服务 API 密钥（例如 SiliconFlow）
  "api-url-tts": "https://api.siliconflow.cn/v1/audio/speech",  // TTS 服务请求地址
  "api-key-llm-1": "",  // 主 LLM API 密钥（主要用于生成主播回复）
  "api-key-llm-2": "sk-",  // 次 LLM API 密钥（用于过滤无意义消息和辅助判断是否需要截屏）
  "api-url-1": "",   // 主 LLM 服务请求地址
  "api-url-2": "https://api.siliconflow.cn/v1/chat/completions",   // 次 LLM 服务请求地址
  "live_url": "https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid=YOURID&room_type=0",  // 将 YOURID 替换为你的 B 站直播间 ID
  "ws_host": "ws://localhost:8088",  // VTuber Studio (VTS) WebSocket 地址
  "vts_authenticationToken": "",  // VTS 认证令牌（可选，留空则首次启动时自动获取）
  "streamer_name":"your name",  // 你的 B 站直播间昵称，有助于 LLM 区分主播和观众
  "use_text_align":false, // 强制文本-语音对齐功能，开启后可实现字幕与语音同步显示（需额外安装 torch 和 whisperx）
  "use_screen_shot":true, //是否启用小模型来辅助判断启用截图功能
  "use_stream":true //是否开启流式输出并生成语音，可能有助于减少AI主播的反应时间
}
```

**注意**：启用 `use_text_align` 功能需要额外安装 PyTorch 相关库和 whisperx，这相对复杂。因此，该选项默认是关闭的。

-----

## ▶️ 如何运行

### 1\. 启动服务

在项目根目录下运行主程序：

```bash
python main.py
```

### 2\. 关键配置步骤

1.  **修改直播间地址**：
    在 `main.py` 文件中，将 `live_url` 变量替换为你的 B 站直播间真实地址：
    ```python
    live_url = "https://live.bilibili.com/your_room_id"  # 请替换为你的直播间地址
    ```
2.  **配置 TTS 模式**：
      * **使用在线 API**：确保 `config.json` 中已正确填写有效的 TTS API 地址和密钥。
      * **使用本地模型**：如果你希望使用本地部署的 TTS 模型，请部署 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 并相应地修改 `main.py` 中的 TTS 调用逻辑。
3.  **自定义主播角色**（可选）：
    在 `main.py` 文件的 `Prompt` 变量中，可以自定义你的 AI 主播角色设定。例如：
    ```text
    你是一个活泼的虚拟偶像，用元气满满的日语和观众互动！
    ```
4.  **文件输出**：
      * 生成的语音文件将统一保存在 `./voices` 文件夹中。
      * 实时处理的文本输出会保存在 `./text/realtime_chars.txt` 文件中。

-----

## 📺 效果展示

  * **演示视频**：点击观看 [B 站直播演示](https://www.bilibili.com/video/BV1EDLhzCE9x/)
  * **界面截图**：

-----

## 🧪 版本更新日志

-----

### Version 0.1 (2025-07-11)

  * 重构 API 调用方式，不再依赖酒馆系统，实现更轻量级的部署。
  * 新增本地 TTS 支持（集成 GPT-SoVITS 模型）。
  * 实现 TTS 响应的持久化存储功能。
  * 优化弹幕过滤逻辑，提高互动质量。

-----

### Version 0.1.1 (2025-07-12)

  * 增加智能截屏功能，并与小模型联合判断回复是否需要截屏操作，增强 AI 决策能力。

-----

### Version 0.1.2 (2025-07-13)

  * 新增强制文本-语音对齐功能，提升直播字幕与语音的同步体验（输出文件位于 `./text` 目录）。
  * 更新了主播人格 Prompt，使 AI 主播的性格更贴合直播场景，并生成更具相关性的弹幕回复。
  * 优化vtuber studio api调用逻辑，使其更加活灵活现。
-----
### Version 0.1.15 (2025-07-15)
  * 增加流式输出

## 📜 许可证

本项目采用 [MIT License](https://github.com/yourusername/bilibili-ai-live-demo/blob/main/LICENSE)。你可以自由地进行商业使用和修改，但请务必保留原作者信息。

-----

如果觉得这个项目对你有帮助，可以点点 **star**！⭐⭐