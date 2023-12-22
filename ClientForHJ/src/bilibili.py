# -*- coding: utf-8 -*-
import asyncio
import blivedm
import blivedm.models.open_live as open_models
import ClientForHJ.cfg.config as config
import socketconn


async def main():
    await run_single_client()


async def run_single_client():
    """
    演示监听一个直播间
    """
    client = blivedm.OpenLiveClient(
        access_key_id=config.ACCESS_KEY_ID,
        access_key_secret=config.ACCESS_KEY_SECRET,
        app_id=config.APP_ID,
        room_owner_auth_code=config.ROOM_OWNER_AUTH_CODE,
    )
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    try:
        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler(blivedm.BaseHandler):
    def _on_open_live_danmaku(self, client: blivedm.OpenLiveClient, message: open_models.DanmakuMessage):
        socketconn.DownloadSend(-11, message.uname, message.uid, message.uface, 0, 0, message.msg)

    def _on_open_live_gift(self, client: blivedm.OpenLiveClient, message: open_models.GiftMessage):
        socketconn.DownloadSend(-12, "", message.uid, "",  message.price * message.gift_num, 0, "")

    def _on_open_live_like(self, client: blivedm.OpenLiveClient, message: open_models.LikeMessage):
        socketconn.DownloadSend(-13, "", message.uid, "",  0, message.like_count, "")


def begin_bilibili_websocket():
    asyncio.run(main())
