import json
def msg_filte(msg):
    with open('./config.json', 'r') as file:
        config = json.load(file)
        return any(keywords in msg for keywords in config['msg_filte'])