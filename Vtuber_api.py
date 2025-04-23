import asyncio
import json
import random
import math
from websockets import connect
# from config import DEFAULT_CONFIG,save_config
current_params = {
    "FaceAngleX": 0,
    "FaceAngleY": 0,
    "EyeLeftX": 0.5,
    "EyeRightX": 0.5,
    "EyeLeftY": 0.5,
    "EyeRightY": 0.5,
    "HandLeftPositionX": 0,
    "HandLeftPositionY": 0
    # "NeckZ": 0 
}
async def get_authenticationToken():
    uri = "ws://localhost:8001"
    async with connect(uri) as socket:
        to_auth = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "123",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": "My Cool Plugin",
                "pluginDeveloper": "My Name",
            }
        }
        await socket.send(json.dumps(to_auth))
        response = json.loads(await socket.recv())
        print('authenticationToken ' + str(response['data']['authenticationToken']))
        with open('./config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            config['vts_authenticationToken'] = str(response['data']['authenticationToken'])
        with open("./config.json",'w',encoding='utf-8') as f:
            json.dump(config, f,ensure_ascii=False)

async def dynamic_gaze():
    global current_params
    with open('config.json', 'r', encoding='utf-8') as f:
        GLOBAL_CONFIG = json.load(f)
        if GLOBAL_CONFIG['vts_authenticationToken'] == '':
            await get_authenticationToken()
    uri = "ws://localhost:8001"
    async with connect(uri) as websocket:
        # 1. 身份认证（需补充你的认证逻辑）
        # ...
        authed = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "123",
        "messageType": "AuthenticationRequest",
        "data": {
            "pluginName": "My Cool Plugin",
            "pluginDeveloper": "My Name",
            "authenticationToken": GLOBAL_CONFIG['vts_authenticationToken']
        }
        }
        await websocket.send(json.dumps(authed))
        auth_response = await websocket.recv()
        print("认证响应:", json.loads(auth_response))
        # 2. 初始化参数


        # 3. 持续随机视线循环
        while True:
            # 生成随机目标（头部和眼睛）
            if GLOBAL_CONFIG['statue'] == 1:
                target = {
                    "FaceAngleX": random.uniform(-20, 20),   # 头部水平转动范围
                    "FaceAngleY": random.uniform(-15, 10),   # 头部垂直转动范围
                    "EyeLeftX":  clamp(random.gauss(0.5, 0.2), 0.2, 0.8),  # 高斯分布更自然
                    "EyeRightX": clamp(random.gauss(0.5, 0.2), 0.2, 0.8),
                    "EyeLeftY":  clamp(random.gauss(0.5, 0.1), 0.3, 0.7),
                    "EyeRightY": clamp(random.gauss(0.5, 0.1), 0.3, 0.7),
                    "HandLeftPositionX": random.uniform(-10, 10),
                    "HandLeftPositionY": random.uniform(-10, 10)
                    
                }
                duration = random.uniform(1, 2.5)  # 随机过渡时间

            else:
                target = {
                    "FaceAngleX": random.uniform(-20, 20)*2,   # 头部水平转动范围
                    "FaceAngleY": random.uniform(-15, 10)*2,   # 头部垂直转动范围
                    "EyeLeftX":  clamp(random.gauss(0.5, 0.2), 0.2, 0.8),  # 高斯分布更自然
                    "EyeRightX": clamp(random.gauss(0.5, 0.2), 0.2, 0.8),
                    "EyeLeftY":  clamp(random.gauss(0.5, 0.1), 0.3, 0.7),
                    "EyeRightY": clamp(random.gauss(0.5, 0.1), 0.3, 0.7),
                    "HandLeftPositionX": random.uniform(-10, 10),
                    "HandLeftPositionY": random.uniform(-10, 10)
                }
            # # 4. 平滑过渡到目标（使用缓动函数）
                duration = random.uniform(0.4, 0.8)  # 随机过渡时间

            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                progress = (asyncio.get_event_loop().time() - start_time) / duration
                # 使用 easeOutQuad 缓动函数
                t = 1 - (1 - progress) ** 2  
                
                # 插值计算当前值
                interpolated = {}
                for key in current_params:
                    interpolated[key] = lerp(current_params[key], target[key], t)
                
                # 添加微小随机抖动（增强灵动感）
                if random.random() < 0.3:
                    interpolated["FaceAngleX"] += random.uniform(-1, 1)
                    interpolated["EyeLeftX"] = clamp(interpolated["EyeLeftX"] + random.uniform(-0.05, 0.05))
                
                # 构建参数列表
                parameters = [
                    {"id": "FaceAngleX", "value": interpolated["FaceAngleX"]},
                    {"id": "FaceAngleY", "value": interpolated["FaceAngleY"]},
                    {"id": "EyeLeftX", "value": interpolated["EyeLeftX"]},
                    {"id": "EyeRightX", "value": interpolated["EyeRightX"]},
                    {"id": "EyeLeftY", "value": interpolated["EyeLeftY"]},
                    {"id": "EyeRightY", "value": interpolated["EyeRightY"]},
                    {"id": "HandLeftPositionX", "value": interpolated["FaceAngleX"]*0.2},
                    {"id": "HandLeftPositionY", "value": interpolated["FaceAngleX"]*0.2}

                ]
                
                # 发送指令
                await websocket.send(json.dumps({
                    "apiName": "VTubeStudioPublicAPI",
                    "apiVersion": "1.0",
                    "requestID": "GazeControl1",
                    "messageType": "InjectParameterDataRequest",
                    "data": {
                        "faceFound": 'false',
                        "mode": "set",
                        "parameterValues": parameters
                        }
                }))
                response = await websocket.recv()
                await asyncio.sleep(0.02)  # 约33fps
                # print('Nomal status'+ str(response))
            # 更新当前状态
            current_params = target.copy()

def lerp(a, b, t):
    """线性插值"""
    return a + (b - a) * t

def clamp(value, min_val=0.0, max_val=1.0):
    """限制数值范围"""
    return max(min_val, min(value, max_val))



async def expressive_head_movement():
    global current_params
    uri = "ws://localhost:8001"
    async with connect(uri) as websocket:
        # 身份认证...
        authed = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "123",
        "messageType": "AuthenticationRequest",
        "data": {
            "pluginName": "My Cool Plugin",
            "pluginDeveloper": "My Name",
            "authenticationToken": "4ed673edc7e48a64ac9ad753c98318c24380f28481dafd3a5c7a822e5abbcb90"
        }
        }
        await websocket.send(json.dumps(authed))
        auth_response = await websocket.recv()
        print("认证响应:", json.loads(auth_response))
        # 初始化参数
        current = {
            "FaceAngleX": current_params['FaceAngleX'], "FaceAngleY": current_params['FaceAngleY'], 
            "EyeLeftX": current_params['EyeLeftX'], "EyeRightX": current_params['EyeRightX'],
            # "NeckZ": 0  # 增加颈部旋转（部分模型支持）
        }

        # 模拟语音节奏参数
        syllable_interval = random.uniform(0.7,0.75)  # 每个音节间隔（秒）
        stress_probability = 0 # 重音概率

        while True:
            # 生成带语音节奏的随机动作
            is_stressed = random.random() < stress_probability
            target = {
                "FaceAngleX": random.uniform(-50, 50) * (1.5 if is_stressed else 1),
                "FaceAngleY": random.uniform(-30, 30) * (1.8 if is_stressed else 0.7),
                "NeckZ": random.uniform(-10, 10),  # 颈部扭转
                "EyeLeftX": clamp(0.5 + random.uniform(-0.4, 0.4)),
                "EyeRightX": clamp(0.5 + random.uniform(-0.4, 0.4))
            }

            # 强化重音动作（如点头/摇头）
            if is_stressed:
                target["FaceAngleY"] += (-25 if random.random() > 0.5 else 15)
                target["FaceAngleX"] *= 1.8

            # 弹性动画（overshoot效果）
            overshoot_factor = 1.2  # 过冲量
            duration = syllable_interval * (0.7 if is_stressed else 1.3)
            
            start_time = asyncio.get_event_loop().time()
            while (elapsed := asyncio.get_event_loop().time() - start_time) < duration:
                # 弹性缓动函数
                progress = elapsed / duration
                if progress < 0.5:
                    t = 2 * progress ** 2  # 加速阶段
                else:
                    t = 1 - 2 * (1 - progress) ** 2  # 减速+回弹
                
                # 计算当前值（带过冲）
                for key in current:
                    delta = target[key] - current[key]
                    if progress < 0.7:  # 主运动阶段
                        current[key] += delta * t * (overshoot_factor if is_stressed else 1)
                    else:  # 回弹阶段
                        current[key] = target[key] + delta * 0.2 * math.sin((progress-0.7)*10)

                # 发送指令
                parameters = [
                    {"id": "FaceAngleX", "value": current["FaceAngleX"]},
                    {"id": "FaceAngleY", "value": current["FaceAngleY"]},
                    # {"id": "NeckZ", "value": current["NeckZ"]},
                    {"id": "EyeLeftX", "value": current["EyeLeftX"]},
                    {"id": "EyeRightX", "value": current["EyeRightX"]}
                ]
                await websocket.send(json.dumps({
                    "apiName": "VTubeStudioPublicAPI",
                    "apiVersion": "1.0",
                    "requestID": "GazeControl1",
                    "messageType": "InjectParameterDataRequest",
                    "data": {
                        "faceFound": 'false',
                        "mode": "set",
                        "parameterValues": parameters}
                }))
                response = await websocket.recv()
                await asyncio.sleep(0.02)  # 50fps保证流畅


            # 随机微休息（模拟呼吸间隔）
            if random.random() < 0.4:
                await asyncio.sleep(random.uniform(0.05, 0.15))

asyncio.run(get_authenticationToken())
# asyncio.run(expressive_head_movement())

