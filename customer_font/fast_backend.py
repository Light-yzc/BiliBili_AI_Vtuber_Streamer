from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
import os
import logging
import uvicorn
# 创建 FastAPI 应用实例
app = FastAPI(
    title="实时字幕服务",
    description="一个简单的 FastAPI 应用，用于从文本文件读取实时字幕并显示在网页上。"
)

# 配置日志，FastAPI 默认会有自己的日志，这里只是为了演示可以单独配置
# 你可以根据需要调整日志级别，例如 logging.INFO, logging.WARNING 等
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取当前脚本的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 构建 text 文件的绝对路径
# 确保 text 文件夹与 main.py 在同一目录下
TEXT_FILE = '../text/realtime_chars.txt'
# 构建 HTML 模板文件的绝对路径
# 确保 templates 文件夹与 main.py 在同一目录下，且 subtitle.html 在 templates 文件夹内
HTML_TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "subtitle.html")

def get_last_line() -> str:
    """高效获取文件最后一行"""
    # 检查文件是否存在
    if not os.path.exists(TEXT_FILE):
        logger.warning(f"字幕文件未找到: {TEXT_FILE}")
        return "字幕文件未找到..."
    
    try:
        with open(TEXT_FILE, 'rb') as f: # 使用二进制读取以处理结尾问题
            # 移动到文件末尾
            f.seek(0, os.SEEK_END)
            # 如果文件为空，直接返回
            if f.tell() == 0:
                return ""
            
            # 向后查找换行符
            file_size = f.tell()
            if file_size < 2: # 文件太小，直接从头开始读
                f.seek(0)
            else:
                f.seek(-2, os.SEEK_END) 
                while f.read(1) != b'\n':
                    if f.tell() == 1: # 如果到了文件开头
                        f.seek(0)
                        break
                    f.seek(-2, os.SEEK_CUR)
            
            # 读取最后一行并解码
            last_line = f.readline().decode('utf-8').strip()
            return last_line if last_line else ""

    except Exception as e:
        logger.error(f"读取文件时出错: {e}", exc_info=True)
        return "读取字幕时出错..."

def load_html_template(file_path: str) -> str:
    """从文件中加载 HTML 模板内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"HTML 模板文件未找到: {file_path}")
        return "<h1>错误：HTML 模板文件未找到！</h1>"
    except Exception as e:
        logger.error(f"加载 HTML 模板时出错: {e}", exc_info=True)
        return "<h1>错误：加载 HTML 模板失败！</h1>"

# 在应用启动时加载 HTML 模板内容
HTML_CONTENT = load_html_template(HTML_TEMPLATE_FILE)

@app.get("/", response_class=HTMLResponse, summary="显示实时字幕页面")
async def read_root():
    """
    根路径，返回包含实时字幕的 HTML 页面。
    该页面通过 JavaScript 定期从 `/get_subtitle` 获取最新文本。
    """
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/get_subtitle", response_class=PlainTextResponse, summary="获取最新字幕文本")
async def get_current_subtitle():
    """
    API 端点，用于获取 `realtime_chars.txt` 文件的最后一行文本。
    """
    return get_last_line()

if __name__ == "__main__":
    print(f"访问地址：http://127.0.0.1:5000/来使用文本服务")
    uvicorn.run(app='fast_backend:app', host='0.0.0.0', port=5000, reload=True, log_level='warning')
# web地址http://127.0.0.1:5000/