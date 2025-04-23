#获取b站弹幕
import requests

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
    params = {
        "roomid": "1862819",
        "room_type": "0"
    }

    response = requests.get(url, headers=headers, params=params)
    return (response.json()['data']['room'][-1]['text'])


