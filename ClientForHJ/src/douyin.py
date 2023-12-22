import datetime
import logging
from datetime import time
import os
import ClientForHJ.cfg.config as config
import env
import ClientForHJ.cfg.static as static
from douyinWebSocket import Douyin

env.init()


def is_not_delete_tiktokPath():
    #增加标志位文件，每次运行判断当前日期和标志位文件的日期是否一致，不一致再删除抖音的爬取头像静态文件，随后更新标志文件。当天的头像静态文件会一直保留
    today = datetime.date.today()
    flag_file = 'flag.txt'
    if not os.path.exists(flag_file):
        open(flag_file, 'w').write(today.strftime('%Y-%m-%d'))

    with open(flag_file) as f:
        last_run_date = datetime.datetime.strptime(f.read(), '%Y-%m-%d').date()

    if today > last_run_date:
        # 删除静态文件
        static.delete_files_in_directory(config.tiktokPath)
        static.delete_files_in_directory(config.BiliBiliPath)

        # 更新标志文件
        with open(flag_file, 'w') as f:
            f.write(today.strftime('%Y-%m-%d'))


def begin_douyin_websocket(sRoomID):
    is_not_delete_tiktokPath()
    url = config.content['url'] + sRoomID
    logging.info(f"远程监听 {url}")
    dy = Douyin(url)
    dy.connect_web_socket()

