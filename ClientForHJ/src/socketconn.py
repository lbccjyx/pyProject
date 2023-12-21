import atexit
import json
import os
import time
import requests
import socket
import struct
import queue
import threading
import pyttsx3
import logging
from PIL import Image


import ClientForHJ.cfg.static as static

address = '127.0.0.1'
port = 0  # 你需要将端口替换为实际的端口号
my_set = set()
data_queue = queue.Queue()
welcome_queue = queue.Queue()
sock = None  # 添加一个全局变量用于保存socket连接
dict_uuid_id = {}
uniqueID = 339988220000



def getRAPort():
    global port
    if port == 0:
        strport = static.read_port_from_file(static.portFilename)
        port = int(strport)
        return port
    return 0


getRAPort()
IsSendToRa = False if port == 0 else True


# 下载后 先压缩 再保存到指定路径 注意保存为png格式  这里的大小要是2的幂次方
def downloadImg(url, path, new_size=(32, 32)):
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as file:
                file.write(r.content)
            r.close()
            image = Image.open(path)
            image = image.resize(new_size)
            image.save(path)
            return True
    except requests.RequestException as e:
        logging.info(f"请求失败：{e}")
    except Exception as e:
        logging.info(f"发生意外错误：{e}")
    return False


def create_connection(address, port):
    global IsSendToRa, sock
    if not IsSendToRa:
        return
    Address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(Address)
    return sock


def close_connection():
    global IsSendToRa, sock
    if not IsSendToRa:
        return
    sock.close()


if IsSendToRa:
    create_connection(address, port)
    # 注册关闭连接的函数
    atexit.register(close_connection)


def send_data(data):
    global IsSendToRa, sock
    if not IsSendToRa:
        return
    sock.sendall(data)


def send_data(data):
    global IsSendToRa, port, sock, data_queue
    if not IsSendToRa:
        return

    sock.sendall(data)



def getScriptDir():
    return os.path.split(os.path.realpath(__file__))[0]


def send_data_from_queue():
    global IsSendToRa, data_queue, port
    if not IsSendToRa:
        return

    while True:
        data = data_queue.get()
        try:
            if data is not None:
                send_data(data)
        except Exception as e:
            logging.info(f"发送数据失败：{e}")
            logging.info("等待2秒后重试...")
            time.sleep(2)
            port = 0
            port = getRAPort()
            # 重新创建连接
            create_connection(address, port)
            data_queue.put(data)


def welcome_from_queue():
    global welcome_queue, IsSendToRa
    if not IsSendToRa:
        return
    MachineSay = pyttsx3.init()
    while True:
        data = welcome_queue.get()
        if data is not None:
            if welcome_queue.qsize() == 0:
                MachineSay.say("欢迎" + data + "来到直播间")
                MachineSay.runAndWait()
            if welcome_queue.qsize() > 0:
                MachineSay.say("欢迎" + data)
                MachineSay.runAndWait()
            continue

        if welcome_queue.empty():
            time.sleep(2)


def is_all_ones(num):
    return set(str(num)) == {'1'}


# 如果是玩家的id抖音都给 111111 那就用 user_name 对应的uuid 对应一个唯一id 返回唯一id 重新作为玩家id
def checkUserID(userID, user_name):
    global dict_uuid_id, uniqueID
    if is_all_ones(userID):
        uid = static.string_to_uuid(user_name)
        if uid in dict_uuid_id:
            return dict_uuid_id[uid]
        uniqueID = uniqueID + 1
        dict_uuid_id[uid] = uniqueID
        return uniqueID
    else:
        return userID


def DouyinDownloadSend(iframe, payload_pack):
    global IsSendToRa, data_queue, my_set, welcome_queue
    user_name = payload_pack.user.nickName if hasattr(payload_pack.user, 'nickName') else ""
    userID = payload_pack.user.id if hasattr(payload_pack.user, 'id') else 0
    userHeaderImg = payload_pack.user.AvatarThumb.urlListList[0] if hasattr(payload_pack.user, 'AvatarThumb') else ""
    gift_name = payload_pack.gift.name if hasattr(payload_pack, 'gift') and hasattr(payload_pack.gift, 'name') else ""
    like_cnt = payload_pack.count if hasattr(payload_pack, 'count') else 0
    content = payload_pack.content if hasattr(payload_pack, 'content') else ""
    # 解决全是1111的id
    userID = checkUserID(userID, user_name)
    if userID not in my_set:
        success = downloadImg(userHeaderImg, f"{static.tiktokPath}\\{userID}.png")
        if not success:
            return
        my_set.add(userID)
    if iframe == -1:
        if len(user_name) > 0:
            welcome_queue.put(payload_pack.user.nickName)
    data = {
        "IUserId": userID,
        "SName": user_name,
        "SPath": f"{userID}.png",
        "SComment": content,
        "SGift": gift_name,
        "NAddLike": like_cnt or 0
    }
    logging.info(f"iframe {iframe}  data:{data}")

    if not IsSendToRa:
        return

    json_data = json.dumps(data)
    data_length = len(json_data) + 4
    frame = iframe
    formatted_len = struct.pack('<I', data_length)  # 将数据长度转换为小端字节序
    formatted_frame = struct.pack('<i', frame)  # 将帧号转换为小端字节序
    json_data_bytes = json_data.encode()  # 将JSON数据编码为字节
    result = formatted_len + formatted_frame + json_data_bytes
    data_queue.put(result)


def DownloadSend(iframe, user_name, userID, userHeaderImg, TotalGift, like_cnt, content):
    global IsSendToRa, data_queue, my_set
    if not IsSendToRa:
        return

    if userID not in my_set:
        success = downloadImg(userHeaderImg, f"{static.BiliBiliPath}\\{userID}.png")
        if not success:
            return
        my_set.add(userID)

    data = {
        "IUserId": userID,
        "SName": user_name,
        "SPath": f"{userID}.png",
        "SComment": content,
        "NTotalGift": TotalGift or 0,
        "NAddLike": like_cnt or 0
    }
    json_data = json.dumps(data)
    data_length = len(json_data) + 4
    frame = iframe
    formatted_len = struct.pack('<I', data_length)  # 将数据长度转换为小端字节序
    formatted_frame = struct.pack('<i', frame)  # 将帧号转换为小端字节序
    json_data_bytes = json_data.encode()  # 将JSON数据编码为字节
    result = formatted_len + formatted_frame + json_data_bytes
    data_queue.put(result)


send_thread = threading.Thread(target=send_data_from_queue)
send_thread.start()
welcome_thread = threading.Thread(target=welcome_from_queue)
welcome_thread.start()
