import requests
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Length": "115",
    "Content-Type": "application/json",
    "Cookie": "session-1a528558=eyJjc3JmVG9rZW4iOiI2MjRjNzc0MDY5NGFhYmVkMDFmNWFlNTFjMjhjNWU5OGY1MGJhOTk3NWMxZmFmNmFjYjE1MzY5Njc2NDk0NzBhIn0=; session-1a528558.sig=1Qi0qTA0SBu9lmwU0NgXhUcYXmA",
    "Host": "127.0.0.1:8000",
    "Origin": "http://127.0.0.1:8000",
    "Sec-Ch-Ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
    "X-Csrf-Token": "624c7740694aabed01f5ae51c28c5e98f50ba9975c1faf6acb1536967649470a",
    "X-Requested-With": "XMLHttpRequest"
}
def get_date(num):
    global headers,browser
    url = 'http://127.0.0.1:8000/api/characters/all'

    data = {
                '':''
            }

    res = requests.post(url = url, headers = headers,json=data)
    msg = { 
        'avatar_url':res.json()[num]['avatar'],
        'file_name':res.json()[num]['chat'],
        'ch_name':res.json()[num]['name']
    }
    return msg

print(get_date(1))