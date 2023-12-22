import gzip
import json
import logging
import os
import re
import websocket
import ClientForHJ.cfg.static as pyconfig
import time
import requests
from protobuf import dy_pb2
import socketconn


class Douyin:
    def __init__(self, url):
        self.ws_conn = None
        self.url = url
        self.room_info = None

    def _send_ask(self, log_id, internal_ext):
        ack_pack = dy_pb2.PushFrame()
        ack_pack.logId = log_id
        ack_pack.payloadType = internal_ext

        data = ack_pack.SerializeToString()
        self.ws_conn.send(data, opcode=websocket.ABNF.OPCODE_BINARY)

    def _on_message(self, ws, message):
        msg_pack = dy_pb2.PushFrame()
        msg_pack.ParseFromString(message)
        decompressed_payload = gzip.decompress(msg_pack.payload)
        payload_package = dy_pb2.Response()
        payload_package.ParseFromString(decompressed_payload)
        if payload_package.needAck:
            self._send_ask(msg_pack.logId, payload_package.internalExt)
        for msg in payload_package.messagesList:
            match msg.method:
                case 'WebcastChatMessage':
                    self._parse_chat_msg(msg.payload)
                case "WebcastGiftMessage":
                    self._parse_gift_msg(msg.payload)
                case "WebcastLikeMessage":
                    self._parse_like_msg(msg.payload)
                case "WebcastMemberMessage":
                    self._parse_member_msg(msg.payload)

    @staticmethod
    def _on_error(ws, error):
        logging.error(error)

    @staticmethod
    def _on_close(ws, close_status_code, close_msg):
        logging.info("Websocket closed")

    @staticmethod
    def _on_open(ws):
        logging.info("Websocket opened")

    @staticmethod
    def _parse_chat_msg(payload):
        payload_pack = dy_pb2.ChatMessage()
        payload_pack.ParseFromString(payload)
        socketconn.DouyinDownloadSend(-2, payload_pack)

    @staticmethod
    def _parse_gift_msg(payload):
        payload_pack = dy_pb2.GiftMessage()
        payload_pack.ParseFromString(payload)
        socketconn.DouyinDownloadSend(-4, payload_pack)

    @staticmethod
    def _parse_like_msg(payload):
        payload_pack = dy_pb2.LikeMessage()
        payload_pack.ParseFromString(payload)
        socketconn.DouyinDownloadSend(-3, payload_pack)

    @staticmethod
    def _parse_member_msg(payload):
        payload_pack = dy_pb2.MemberMessage()
        payload_pack.ParseFromString(payload)
        socketconn.DouyinDownloadSend(-1, payload_pack)

    def _get_room_info(self):
        payload = {}
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent':  pyconfig.content['douyin']['user_agent'] +
                          pyconfig.content['douyin']['user_agent1'],
            'cookie': '__ac_nonce=0638733a400869171be51',
        }

        proxies = dict(http="", https="")

        response = requests.get(self.url, headers=headers, data=payload, proxies=proxies)
        res_cookies = response.cookies
        ttwid = res_cookies.get_dict().get("ttwid")
        res_origin_text = response.text
        re_pattern = pyconfig.content['douyin']['re_pattern']
        re_obj = re.compile(re_pattern)
        matches = re_obj.findall(res_origin_text)
        for match_text in matches:
            try:
                match_json_text = json.loads(f'"{match_text}"')
                match_json = json.loads(match_json_text)
                if match_json.get('state') is None:
                    continue
                room_id = match_json.get('state').get('roomStore').get('roomInfo').get('roomId')
                room_title = match_json.get('state').get('roomStore').get('roomInfo').get('room').get('title')
                room_user_count = match_json.get('state').get('roomStore').get('roomInfo').get('room').get(
                    'user_count_str')
                unique_id = match_json.get('state').get('userStore').get('odin').get('user_unique_id')
                avatar = match_json.get('state').get('roomStore').get('roomInfo').get('anchor').get('avatar_thumb').get(
                    'url_list')[0]
                self.room_info = {
                    'url': self.url,
                    'ttwid': ttwid,
                    'room_id': room_id,
                    'room_title': room_title,
                    'room_user_count': room_user_count,
                    'unique_id': unique_id,
                    'avatar': avatar,
                }
            except Exception:
                self.room_info = None

    def CreateDirForPic(self):
        if not os.path.isdir(socketconn.getScriptDir() + "\\userImages"):
            os.makedirs(socketconn.getScriptDir() + "\\userImages")

    def connect_web_socket(self):
        self.CreateDirForPic()
        attempts = 0
        while attempts < 10:
            self._get_room_info()
            if self.room_info is not None:
                break
            else:
                logging.error(f"等待2秒 再次重连 第{attempts+1}次重连中")
                attempts += 1
                time.sleep(2)
            if attempts == 10:
                logging.error(f"获取直播间({self.url})信息失败")
                return

        now = str(time.time_ns() // 1000000)
        ws_url = pyconfig.content['douyin']['ws_origin_url'].replace('${room_id}', self.room_info.get('room_id')).replace(
            '${unique_id}', self.room_info.get('unique_id')).replace('${now}', now)
        headers = {
            'cookie': 'ttwid=' + self.room_info.get('ttwid'),
            'user-agent': pyconfig.content['douyin']['user_agent'] +
                          pyconfig.content['douyin']['user_agent1']
        }

        websocket.enableTrace(False)
        self.ws_conn = websocket.WebSocketApp(ws_url,
                                              header=headers,
                                              on_message=lambda ws, message: self._on_message(ws, message),
                                              on_open=self._on_open,
                                              on_error=self._on_error,
                                              on_close=self._on_close)
        self.ws_conn.run_forever(reconnect=1)

