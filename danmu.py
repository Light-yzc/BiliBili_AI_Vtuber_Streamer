#获取b站弹幕
import requests
import json
from config import app_config
with open('./config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)

logger = app_config.logger
danmu_context = config['danmu_context']
headers = {
    # Regular headers
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cookie': 'buvid3=DCF040B1-A93F-7163-B6A6-206CFB2745CF83420infoc; b_nut=1740986583; _uuid=F5E52102A-5353-5210F-F1F2-E2289F644D2F83814infoc; enable_web_push=DISABLE; buvid4=548FCC0D-AC83-75FF-1118-23DAB6649B5036387-023102921-OuD1af3VG91qRmx5xdZORA%3D%3D; DedeUserID=54824703; DedeUserID__ckMd5=8b030a2378fa0697; hit-dyn-v2=1; rpdid=0zbfAEzD33|1d0DV72|cJm|3w1TP09k; header_theme_version=CLOSE; LIVE_BUVID=AUTO6817410983017740; enable_feed_channel=ENABLE; buvid_fp_plain=undefined; CURRENT_QUALITY=80; blackside_state=0; CURRENT_BLACKGAP=0; fingerprint=7bcafe8b0bee5e8e76daf5c627709452; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDUyOTc5MjIsImlhdCI6MTc0NTAzODY2MiwicGx0IjotMX0.Zn9MHkphzt9wR6p_EjQODA1C1T1vcO_BQ-RvNPnfIs0; bili_ticket_expires=1745297862; SESSDATA=64fd2ae4%2C1760595595%2C92d7e%2A41CjD36lIwJJ7n1QUGt4XetepWtBUW24fufATji7xCt0y6xZx-4gGIgbwdE4YqcmHCGhISVkg5WGlOVDNIOUFDYjYxMlQ4cTBnWFlZSE9KV3JnX0JmVkR5MGdtREJKOWtTRXk2a0ExeE5vM3BQcFFEdDNmeXMtV1libldvZGRpY043dlBScFM3b29nIIEC; bili_jct=2c6368170e8afa233513b6fcd3fceb99; sid=6by53x10; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1743859124,1743941866,1744955219,1745050545; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1745050545; HMACCOUNT=7FCF8321D018E56D; browser_resolution=1528-738; b_lsid=B3A21A510_1964E489414; bsource=search_bing; bp_t_offset_54824703=1057571194821148672; PVID=17; buvid_fp=7bcafe8b0bee5e8e76daf5c627709452; CURRENT_FNVAL=4048',
    'origin': 'https://live.bilibili.com',
    'priority': 'u=1, i',
    'referer': 'https://live.bilibili.com/1862819?visit_id=cstyhhhs51c0',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'
}

# Usage example:
def get_danmu(url):

    response = requests.get(url, headers=headers)
    data = response.json()

    try:
        # 提取弹幕内容
        danmu = []
        user_name = []
        danmu_len = len(data['data']['room'])  # 获取弹幕的总数
        cur_msg = data['data']['room'][-1]['text']
        if not msg_filte(cur_msg):
            logger.warning(f"检测到过滤词在: {cur_msg}")
            return '', '', '<<BAD MSG>>'
        if danmu_context > 1:
            msg_len = max(0, danmu_len - danmu_context)  # 取最近4条弹幕
            for i in range(danmu_len-1, msg_len-1, -1):
                if 'text' in data['data']['room'][i] and data['data']['room'][i]['text']:
                    danmu.append(data['data']['room'][i]['text'])
                    user_name.append(data['data']['room'][i]['nickname'])

            # 提示词模板
            msg = '''
            以下是直播弹幕对话的上下文，最新的弹幕为主要回复内容，其他为上下文。请遵循以下规则进行回复：

            1. **[主要弹幕]** (最新的弹幕): {user1}：{content1}  
            这是最重要的弹幕，请优先回复这一条。如果没有明确的问题或请求，回答时应基于这条弹幕的主题、情感或者讨论内容。如果没有相关的上下文支持，保持回复聚焦于这条弹幕。

            2. **[上下文1]** (倒数第二条弹幕): {user2}：{content2}   
            如果这条弹幕与最新的弹幕有直接的联系或提供了有用的背景信息，请结合它来扩展你的回复。如果没有直接关联，则不需要考虑这条信息。

            3. **[上下文2]** (倒数第三条弹幕): {user3}：{content3}  
            同样，如果这条信息有助于丰富对话背景或解释最新弹幕的意思，请将其纳入回复。否则，可以忽略这条信息，继续专注于最新弹幕。

            4. **[上下文3]** (更早的弹幕): {user4}：{content4}   
            如果这条信息与当前对话主题不相关，可以忽略它。如果它提供了某些历史背景或者情感线索，可以作为参考，但仍然应当优先根据最新的弹幕生成回复。

            **总结**: 请确保回复的焦点始终保持在最新的弹幕内容上。如果之前的弹幕提供了直接的相关背景或补充信息，才可以考虑引用这些信息；否则，回复应该只基于最新的弹幕。

            ---

            **示例**：

            1. **[主要弹幕]**: user1："今天的比赛真是太精彩了！大家觉得哪一队最强？"
            2. **[上下文1]**: user2："我觉得红队的进攻特别强，尤其是那个前锋，简直无敌！"
            3. **[上下文2]**: user3："蓝队虽然防守不错，但似乎进攻有点乏力。"
            4. **[上下文3]**: user4："大家快来投票选出你们心中的MVP吧！"

            **回复**:  
            这条“今天的比赛真是太精彩了！大家觉得哪一队最强？”是最新的弹幕，因此你应主要围绕这个问题进行回答。如果你认为红队进攻强这一上下文与问题相关，可以提到红队的表现如何出色，或者补充蓝队防守的信息。

            ---

            **格式说明**：
            - **[主要弹幕]**：最新的弹幕内容，最重要，优先回复。
            - **[上下文X]**：每条历史弹幕的内容，按时间顺序排列。只有当它们与最新弹幕相关时才应在回复中引用。
            - 每条弹幕包括 **用户名字** 和 **内容**，格式为 `user: content`。
            - 在没有相关上下文时，可以忽略较早的弹幕，只关注最新的弹幕内容进行回复。
    '''

            # 创建一个字典来填充模板
            danmu_dict = {
                "content1": danmu[0] if len(danmu) > 0 else "暂无弹幕",
                "content2": danmu[1] if len(danmu) > 1 else "暂无更多历史弹幕",
                "content3": danmu[2] if len(danmu) > 2 else "暂无更多历史弹幕",
                "content4": danmu[3] if len(danmu) > 3 else "暂无更多历史弹幕",
                "user1": user_name[0] if len(user_name) > 0 else "暂无用户名",
                "user2": user_name[1] if len(user_name) > 1 else "暂无用户名",
                "user3": user_name[2] if len(user_name) > 2 else "暂无用户名",
                "user4": user_name[3] if len(user_name) > 3 else "暂无用户名",
            }

            # 动态填充msg模板
            msg = msg.format(**danmu_dict)

            return (data['data']['room'][-1]['timeline'], data['data']['room'][-1]['nickname'], cur_msg, msg)
        else:
            return (data['data']['room'][-1]['timeline'], data['data']['room'][-1]['nickname'], cur_msg, None)
    except Exception as e:
        logger.warning(e)
        return '', '' , '', ''
    
def msg_filte(msg):

        # return any(keywords in msg for keywords in config['msg_filte'])
    for keywords in config['msg_filte']:
        if keywords in msg:
            return False
    return True
    
# print(get_danmu('https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid=1862819&room_type=0'))

        # print(data['data']['room'])
        # return (data['data']['room'][-1]['timeline'], data['data']['room'][-1]['nickname'], data['data']['room'][-1]['text'])

# print(msg_filte('1233'))