import os
import sys
import uuid

tiktokPath = "D:\\notes\\duties\\gitTest\\ra2\\mods\\ra2\\uibits\\tiktok"
BiliBiliPath = "D:\\notes\\duties\\gitTest\\ra2\\mods\\ra2\\uibits\\bilibili"
appdata = os.environ['APPDATA']
portFilename = os.path.join(appdata, 'OpenRA', 'CGamePort.txt')
#portFilename = r"C:\Users\a\AppData\Roaming\OpenRA\CGamePort.txt"


def read_port_from_file(Filename):
    try:
        with open(Filename, 'r') as file:
            port = file.readline().strip()
        return port
    except FileNotFoundError:
        print(f"文件 {Filename} 不存在.")
        return 0


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def delete_files_in_directory(directory_path):
    try:
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")


namespace = uuid.NAMESPACE_DNS


def string_to_uuid(name):
    return uuid.uuid3(namespace, name)
