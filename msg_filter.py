from config import GLOBAL_CONFIG
def msg_filte(msg):
    return any(keywords in msg for keywords in GLOBAL_CONFIG['msg_filte'])