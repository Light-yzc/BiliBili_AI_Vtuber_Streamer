import requests
import json
url = 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions'
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer AIzaSyBGxoyRa70hkQQyzg0eXsfCCRAZCGGbzrU"
}
payload_tmp = []
payload_tmp.append({
            "role": "user",
            "content":'你好',
            })
payload = {
    "model": 'gemini-2.5-flash',
    "messages": payload_tmp,
    "stream":True
    }
# response = requests.post(url, headers=headers, data=json.dumps(payload))
# print(response.text)
with requests.post(url, headers=headers, data=json.dumps(payload), stream=True) as response:
    for line in response.iter_lines(chunk_size=256):

        if line:
            decode_line = line.decode('utf-8')
            # print(decode_line)
            if decode_line[:5] == "data:":
                event_data = decode_line[5:].strip()
                if event_data == "[DONE]":  # 流结束
                    break
                chunk = json.loads(event_data)
                if "content" in chunk["choices"][0]["delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    print(content, end='')