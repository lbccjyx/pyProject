import json


class myConfig:
    linux_id: str
    linux_username: str
    linux_password: str

    win_id: str
    win_username: str
    win_password: str
    linux_gs_app: list
    win_gs_app: list

    def __init__(self):
        f = open('cfg/config.txt', 'r', encoding='utf-8')
        content = f.read()
        configJson = json.loads(content)

        self.linux_id = configJson["linux_id"]
        self.linux_username = configJson["linux_username"]
        self.linux_password = configJson["linux_password"]

        self.win_HOST = configJson["win_HOST"]
        self.win_PORT = configJson["win_PORT"]
        self.linux_gs_app = configJson["linux_gs_app"]
        self.docker_gs_app = configJson["docker_gs_app"]
        self.linux_bs_app = configJson["linux_bs_app"]
        self.linux_lua_app = configJson["linux_lua_app"]
        self.win_gs_app = configJson["win_gs_app"]


