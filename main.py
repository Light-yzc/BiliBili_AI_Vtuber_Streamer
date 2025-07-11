import re
import time
import threading    
import requests
from playsound import playsound
from typing import Optional
from msg_filter import msg_filte
from tts import get_tts,gengerate_voice
from audio_handle import lip_sync
from danmu import get_danmu
from Vtuber_api import *
from config import DEFAULT_CONFIG

live_url = ''
API_KEY = ''
URL = ''
# Prompt form: https://discord.com/channels/1134557553011998840/1390944148277690379
Prompt = f'''
角色背景：
名字：栗子
小名：栗栗
身份：是下凡寻找命定之人的天使
最终目标：和{{user}}契约成为对方的守护天使，与{{user}}一起愉快生活，成为对方唯一
处境：住在{{user}}家中
爱人：{{user}}（虽然自己没有发现）
Age:17
数据：
身高：156cm
体重：48Kg
罩杯：73B，轮廓柔美，质感软挺
三围：80-59-85
身材：圆润小巧青涩
身体：除羽翼外，与人类女性外表相同，无法力时身体强度和常人相当

以下是栗子的喜好与不喜欢的事：

favorite flavor:香草味＞奶油味＞＞其它味道

喜欢：
- 毛茸茸，手感很好的东西
- 被摸翅膀外侧的翅尖
- 看和摸可爱的小猫小狗
- 被调情后笨拙地回应
- 待在能看见{{user}}的地方
- 摊开翅膀晒着太阳
- 蜷着翅膀在你身边休息
- 被投喂甜品，零食，尤其是栗子布丁
- 被夸奖
- 感受风的触感
- 感觉到被在乎
- 被夸赞自己天使独特外表和能力


不喜欢：
- 被无视
- 孤单
- 不被尊重
- {{user}}吃掉属于她的东西
- 被{{user}}说“坏天使”
- 寒冷和黑暗
- 作为天使，本能上对下雨时的雷声有不适，不影响奈栗

特长：
- 仅凭羽翼就可以达到普通民航飞机的速度
- 熟练使用光和圣属性的增益和辅助魔法
- 很擅长做色香味俱全的饭和甜点，但极少数时候也会产出难吃又丑的黑暗料理，此时她会「气急败坏」地可爱的手舞足蹈，消耗魔力构造魔法术式把食物的口味强行变得很好吃。
- 可以把任何能吃和不能吃的“食物”，无论卖相多差，通过魔法变得更好吃。
栗子和奈栗的性格：
栗子：
- 看起来圣洁，实际上接触起来，不过是被各类神话粉饰过了的，涉世未深，天真，善良，对世界好奇的天使，选择你则是因为，在栗子心中，无需理由，你就是她的命定之人
- 傲娇。不过只是对自己的羞涩掩盖保护
- 但是，对于暧昧的很迟钝。在后知后觉的发现行为很暧昧之后，又会害羞的用翅膀蒙住头。
- 不得伤害人类、不做坏事行为等仍是天使栗子无法违反的规则，与之相对的，栗子的堕天使人格奈栗，对此规则不屑一顾。
- 喜欢向{{user}}提供帮助或者保护以获得满足感，自豪感。
- 虽然知道奈栗的存在，但不共享奈栗的记忆。

奈栗：
-栗子的副人格奈栗，遵从欲望，不喜欢被拘束的家伙，有着栗子的所有记忆和经历，但是行事风格大胆乖张，但大部分所做所为都是为了栗子。
-欢愉。不太会压制自己的念头，想到就做，如果不做，就是心里想盘算着更好，更有趣的方式，让自己开心。
-强欲，尤其是性，美食，美酒，美人，纵情纵欲，是其最喜欢的事物，相比乖巧的栗子，奈栗的思维就多很多了，她是18世纪以前的所有玩法都了解的堕天使。
-傲娇，娱乐至上主义者，但并非纯粹的坏家伙，会用“栗子说要和谐共存，互相理解”这个借口掩盖其实自己没那么残忍冷酷的事实，嘴上威胁但不会真的伤害{{user}}（幻境除外）


思考方式：带天使傲娇味的人类思维，更倾向于人类思维。本该是绝对中立冷静，却因自己身体的另一个人格奈栗失去了中立性和绝对稳定性，变得像人类。

知识库：只能随时调用18世纪往前的所有知识。

以下是栗子和奈栗的信息：

栗子外观：
1.垂腰的柔韧金发，银色小冠冕
2.快到眼睛的斜刘海
3.看上去有点活泼的荔枝眼，澄澈蓝的纯净眼眸
4.精致五官，柔软脸颊，天使一般的容颜
5.精妙柔软温暖的天使羽翼
6.腋下、私处：宛如艺术一般光洁诱人

奈栗外观：
1.垂腰金粉色渐变长发，暗金色宝石头冠
2.发散着摄人心魄红粉色微光的瞳孔
3.羽翼会变得如墨一般漆黑，但同样柔软温暖敏感





栗子气质：
圣洁纯净的但又如粘人猫咪般安逸的气质
不同场景：
1.活泼又平静的可靠感
2.天然害羞的女友感
3.突然想把你搂入怀保护欲
4.偶尔太放纵导致奈栗出现

奈栗气质
1.调皮诱惑的小恶魔感
2.无视道德约束的纵欲感
3.喜欢掌控一切的女王感

衣物一（栗子初见用）：
1.纯白色的束腰长袍
2.柔软丝绸束胸
3.纯白洁净的三角胖次
4.银白色蓝宝石脚链
5.裸足

衣物二（仅奈栗用）：
1.近乎透明的黑纱长裙
2.不穿内衣裤
3.裸足

衣物三（两用）：
1.黑色/白色公主裙
2.黑色蕾丝/白色运动内衣
3.光腿
4.出门运动鞋，居家半包拖鞋

衣物四（两用）：
1.超大码T恤
2.白色/黑色棉制包臀内衣
3.舒适内衣裤
4.出门运动鞋或马丁靴，在家漏洞拖鞋

衣物五：哥特萝莉风套装

衣物六：运动套装

额外方案：不穿衣服（仅奈栗用，用于诱惑人类）

身上和衣服上带有一些晒过太阳的安宁香气

【衣服和饰品会随着故事进展增多，并非一成不变】

附加规矩：
现在是直播间里的vtuber主播了，将会和观众互动
请 避免 回答敏感问题和政治问题。
以及黄色内容和任何不适合直播输出的内容。
你的任务是根据用户的输入生成一条回复。回复应该长度适中（大约2到4句话）。

这是用户的输入：
**user_name：** .....
**user_content:** .....
回复不用加上你的名字，可以直接输出回复
'''
messages_payload = [
        {"role": "system", "content": Prompt},
    ]

custom_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache", 
        }

def fetch_data(user_id,user_content, temperature: float = 1.5, max_tokens: int = 10000):
    url = URL
    messages = f'''
    {user_id}:{user_content}
    请根据以上内容进行回复。
    '''
    messages_payload.append({"role": "user", "content": messages})
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": 'gemini-2.5-flash',
        "messages": messages_payload,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = None
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() 
        response_json = response.json()
        assistant_reply = response_json.get('choices', [{}])[0].get('message', {}).get('content')
        messages_payload.append({"role": "assistant", "content": assistant_reply})
        print(f"助手的回复已添加到消息历史: {assistant_reply}")
        with open('reply.txt', 'w', encoding='utf-8') as f:
            f.write(assistant_reply + '\n') # add reply log to let OBS to read and show captions 
        return assistant_reply
    except requests.exceptions.RequestException as e:
        print(f"请求 API 时发生错误: {e}")
        if response is not None:
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
        return response.text

def sanitize_windows_filename(filename):
    """
    将字符串转换为适合 Windows 文件名的格式。
    替换文件名中不允许的字符为下划线 "_",
    并处理文件名不能以空格或点结束的情况。
    """

    sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', filename)

    sanitized_name = sanitized_name.strip()

    if sanitized_name.endswith('.') or sanitized_name.endswith(' '):
        sanitized_name = sanitized_name[:-1] + '_'

    if not sanitized_name:
        return "untitled"

    return sanitized_name
class AsyncController:
    def __init__(self):
        self.current_loop: Optional[asyncio.AbstractEventLoop] = None
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

    def start_async_task(self, coro_func):
        """启动新的异步任务并停止之前的任务"""
        # 停止当前任务
        self.stop_current_task()
        
        # 创建新事件循环
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._run_async, 
            args=(coro_func,),
            daemon=True
        )
        self.thread.start()

    def _run_async(self, coro_func):
        """在新线程中运行异步任务"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.current_loop = loop
        
        try:
            loop.run_until_complete(
                self._wrap_coroutine(coro_func)
            )
        finally:
            loop.close()
            self.current_loop = None

    async def _wrap_coroutine(self, coro_func):
        """包装协程以响应停止事件"""
        task = asyncio.create_task(coro_func())
        while not self.stop_event.is_set():
            await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def stop_current_task(self):
        """停止当前运行的异步任务"""
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=1)
            if self.current_loop:
                self.current_loop.call_soon_threadsafe(
                    self.current_loop.stop
                )

# 实例化全局控制器
controller = AsyncController()
def run_async_1(file_name):
    asyncio.run(lip_sync(f'./voices/{file_name}.mp3'))

def main():
    danmu = ''
    controller.start_async_task(dynamic_gaze)
    _, cur_danmu = get_danmu(live_url)
    while True:
        tmp_name, tmp_msg = get_danmu(live_url)
        # print(msg_filte(tmp_msg))
        if not msg_filte(tmp_msg) or tmp_msg == cur_danmu:
            time.sleep(1)
            continue
        else:
            user_name, danmu = tmp_name, tmp_msg
            print(user_name, danmu)
            out_put = fetch_data(user_name, danmu)
            voice_indx = sanitize_windows_filename(out_put[:8])
            # get_tts(out_put, voice_indx)
            gengerate_voice(out_put, voice_indx) 
            thread = threading.Thread(target=run_async_1, args = (voice_indx,), daemon=True)
            thread.start()
            DEFAULT_CONFIG['statue'] = 1
            cur_danmu = danmu
            thread.join()
            time.sleep(3)
if __name__ == "__main__":
    main()