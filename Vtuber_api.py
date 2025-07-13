import asyncio
import json
import random
import math
from websockets import connect
from config import app_config
with open('./config.json', 'r', encoding='utf-8') as file:
    uri= json.load(file)['ws_host']
current_params = {
    "FaceAngleX": 0,
    "FaceAngleY": 0,
    "EyeLeftX": 0.5,
    "EyeRightX": 0.5,
    "EyeLeftY": 0.5,
    "EyeRightY": 0.5,
    "HandLeftPositionX": 0,
    "HandLeftPositionY": 0,
}
async def get_authenticationToken():
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


#version 1
async def dynamic_gaze():
    global current_params
    with open('config.json', 'r', encoding='utf-8') as f:
        GLOBAL_CONFIG = json.load(f)
        if GLOBAL_CONFIG['vts_authenticationToken'] == '':
            await get_authenticationToken()
    async with connect(uri) as websocket:
        # 1. 身份认证（需补充你的认证逻辑）
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
                # print(response)
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

async def dynamic_gaze_exaggerated():
    """
    一个让VTube Studio模型进行夸张、生动、自然动作的异步函数。
    """
    global current_params
    with open('config.json', 'r', encoding='utf-8') as f:
        GLOBAL_CONFIG = json.load(f)
        # if GLOBAL_CONFIG['vts_authenticationToken'] == '':
        #     await get_authenticationToken()
    
    async with connect(uri) as websocket:
        # 1. 身份认证 (省略，与之前相同)
        # ...
        authed = { "apiName": "VTubeStudioPublicAPI", "apiVersion": "1.0", "requestID": "123", "messageType": "AuthenticationRequest", "data": { "pluginName": "My Cool Plugin", "pluginDeveloper": "My Name", "authenticationToken": GLOBAL_CONFIG['vts_authenticationToken'] } }
        await websocket.send(json.dumps(authed))
        auth_response = await websocket.recv()
        print("认证响应:", json.loads(auth_response))


        # 2. 持续生成并执行夸张动作
        while True:
            target = {} 
            duration = 1.0 

            # --- 动作决策逻辑 ---
            if random.random() < 0.20:
                # --- 动作1: 快速眨眼 (逻辑不变) ---
                target = current_params.copy() 
                target["EyeOpenLeft"] = 0
                target["EyeOpenRight"] = 0
                duration = random.uniform(0.04, 0.045)
            
            else:
                # --- 动作2: 头部与眼睛联动的晃动 ---
                target["EyeOpenLeft"] = 1
                target["EyeOpenRight"] = 1

                # 夸张的头部转动范围
                target["FaceAngleX"] = random.uniform(-35, 35) * app_config.Action_magnification
                target["FaceAngleY"] = random.uniform(-25, 20) * app_config.Action_magnification
                target["FaceAngleZ"] = random.uniform(-30, 30) * app_config.Action_magnification
            
                # <<< --- 核心修改：眼睛联动逻辑 --- >>>
                
                # 1. 将头部角度(-35到35)映射到眼睛范围(0到1)
                #    我们不直接用-35到35，而是用一个稍小的范围如-25到25来映射，
                #    这样当头转到最边上时，眼睛会更早“看”到极限，效果更明显。
                head_x_for_eyes = clamp(target["FaceAngleX"], -25, 25)
                head_y_for_eyes = clamp(target["FaceAngleY"], -20, 20)

                # 2. 计算基础的眼睛朝向
                #    公式: (当前值 - 范围最小值) / (范围最大值 - 范围最小值)
                base_eye_x = ((head_x_for_eyes - (-25)) / (25 - (-25)) * 2 - 1) * 0.5 # 映射到 0-1
                base_eye_y = (head_y_for_eyes - (-20)) / (20 - (-20))# 映射到 0-1

                # 3. 增加自然的随机偏移，模拟视线微小扫动
                random_offset_x = random.uniform(-0.15, 0.15)
                random_offset_y = random.uniform(-0.1, 0.1)

                # 4. 计算最终的眼睛参数，并用 clamp 确保不会超出 0-1 范围
                target["EyeLeftX"] = clamp(base_eye_x + random_offset_x, -0.8, 0.8)
                target["EyeRightX"] = target["EyeLeftX"] # 双眼同步
                
                target["EyeLeftY"] = clamp(base_eye_y + random_offset_y, -0.8, 0.8)
                target["EyeRightY"] = target["EyeLeftY"] # 双眼同步

                # 手部动作
                hand_x_from_head = target["FaceAngleX"] * 0.3
                target["HandLeftPositionX"] = hand_x_from_head + random.uniform(-2, 2)
                target["HandLeftPositionY"] = target["FaceAngleY"] * 0.2 + random.uniform(-3, 3)
                duration = random.uniform(app_config.motion_duriation_min, app_config.motion_duriation_max)
                # duration = random.uniform(0.4, 1.2)
            
            # --- 平滑过渡到目标 (后续逻辑完全不变) ---
            start_time = asyncio.get_event_loop().time()
            start_params = current_params.copy()

            while (asyncio.get_event_loop().time() - start_time) < duration:
                progress = (asyncio.get_event_loop().time() - start_time) / duration
                t = 1 - (1 - progress) ** 3  

                interpolated = {}
                for key in target:
                    if key in start_params:
                        interpolated[key] = lerp(start_params[key], target[key], t)
                    else:
                        interpolated[key] = target[key]

                if random.random() < 0.3:
                    interpolated["FaceAngleX"] += random.uniform(-1.5, 1.5)
                
                parameters = [{"id": key, "value": value} for key, value in interpolated.items()]
                
                await websocket.send(json.dumps({
                    "apiName": "VTubeStudioPublicAPI", "apiVersion": "1.0",
                    "requestID": "GazeControlLinked", "messageType": "InjectParameterDataRequest",
                    "data": { "mode": "set", "parameterValues": parameters }
                }))
                await websocket.recv() # 必须接收响应
                await asyncio.sleep(1/60)

            current_params = target.copy()
            # await asyncio.sleep(random.uniform(0.2, 0.8))
            pause_duration = random.uniform(app_config.pause_duration_min, app_config.pause_duration_max)

            
            pause_start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - pause_start_time) < pause_duration:
                # 在停顿期间持续发送最后的目标参数，防止模型回到默认姿态
                parameters = [{"id": key, "value": value} for key, value in current_params.items()]
                await websocket.send(json.dumps({
                    "apiName": "VTubeStudioPublicAPI", "apiVersion": "1.0",
                    "requestID": "GazeControlLinked", "messageType": "InjectParameterDataRequest",
                    "data": { "mode": "set", "parameterValues": parameters }
                }))
                await websocket.recv() # 必须接收响应
                await asyncio.sleep(1/60) # 保持高帧率以保证平滑



# asyncio.run(get_authenticationToken())
# asyncio.run(dynamic_gaze())
# asyncio.run(dynamic_gaze_exaggerated())