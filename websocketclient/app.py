import tkinter as tk
import websocket
import threading
import sys

lines = []
circles = []
canvas = None
root = None
initialized_event = threading.Event()
nStaticWidth = 130
nStaticLength = 80
nStaticCircle = 120
nStaticCircleRadius = 50
max_per_column = 4
root_startx, root_starty = 0, 0
snap_distance = 50  # 吸附距离

def on_configure(event):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    new_x = root.winfo_x()
    new_y = root.winfo_y()

    if abs(new_x) < snap_distance:
        new_x = 0
        root.geometry(f"1x{window_height}+{new_x}+{new_y}")
    elif abs(new_x + window_width - screen_width) < snap_distance:
        new_x = screen_width - 1
        root.geometry(f"1x{window_height}+{new_x}+{new_y}")

    if abs(new_y) < snap_distance:
        new_y = 0
        root.geometry(f"{window_width}x1+{new_x}+{new_y}")
    elif abs(new_y + window_height - screen_height) < snap_distance:
        new_y = screen_height - 1
        root.geometry(f"{window_width}x1+{new_x}+{new_y}")

def on_click_root(event):
    global root_startx, root_starty
    root_startx, root_starty = event.x_root, event.y_root

class Circle:
    def __init__(self, canvas, x, y, name, num):
        self.name = name
        self.circle = canvas.create_oval(x + nStaticCircleRadius*3 , y, x + nStaticCircleRadius*4, y + nStaticCircleRadius, fill="green")
        self.text = canvas.create_text(x+ nStaticCircleRadius, y+ nStaticCircleRadius//2, text=name)
        self.num = num

    def set_status(self, status):
        if status == '1':
            color = "yellow"
        elif status == '0':
            color = "green"
        elif status == '2':
            color = "red"
        canvas.itemconfig(self.circle, fill=color)


# 发送锁定序号
def on_click(event, ws, circle):
    ws.send(f"lock{circle.num}")


# 接受锁定串
def on_message(ws, message):
    global lines
    global circles
    global canvas
    global root

    if len(lines) <= 0 and message.startswith("HereAreYou ") and len(circles) == 0:
        # 移除前缀，并使用空格分割剩余部分
        lines = message.split("HereAreYou ")[1].split()
        if len(lines) <= 0:
            sys.exit(1)

        nHigh = max_per_column*nStaticLength if len(lines) > max_per_column else len(lines) * nStaticLength
        nWith = nStaticWidth if len(lines) // max_per_column < 1 else (len(lines) // max_per_column + 1) * nStaticWidth
        nWith = nWith*2
        root.geometry(f"{nWith}x{nHigh}")  # 设置窗口大小和位置
        #root.wm_attributes('-transparentcolor', root['bg'])
        canvas = tk.Canvas(root, width=nWith, height=nHigh, highlightthickness=0)
        canvas.pack()

        for i, name in enumerate(lines):
            column = i // max_per_column
            row = i % max_per_column
            x = column * nStaticWidth + 10
            y = row * nStaticLength + 10
            circle = Circle(canvas, x*2 , y, name, i)
            circles.append(circle)
            canvas.tag_bind(circle.circle, '<Button-1>', lambda event, c=circle: on_click(event, ws, c))
        # 使用 root.after 更新 Tkinter 界面
        root.after(0, root.update)

    if len(lines) > 0 and message.isdigit() and len(message) == len(circles):
        for i, circle in enumerate(circles):
            circle.set_status(message[i])

    if message == "bye":
        sys.exit(0)

    if message == "hurry up":
        show_popup()

def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("Connection closed")


def on_open(ws):
    message = "Hello, WebSocket!"
    ws.send(message)


def show_popup():
    popup = tk.Toplevel(root)
    popup.title("hurry up")
    popup.geometry("200x100")
    tk.Label(popup, text="能不能快点啊!").pack(pady=20)
    tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

def run_ws(ws):
    try:
        ws.run_forever()
        root.after(0, root.quit)
    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == "__main__":

    # 创建Tkinter窗口
    root = tk.Tk()
    # 创建一个顶层窗体用于检测点击和拖动
    top_frame = tk.Frame(root)
    top_frame.pack(fill=tk.BOTH, expand=True)

    # 绑定<Configure>事件
    root.bind('<Configure>', on_configure)

    uri = "ws://192.168.1.78:9002"
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(uri,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # 在主线程中尝试连接 WebSocket
    try:
        # 尝试连接 WebSocket
        test_ws = websocket.create_connection(uri)
        test_ws.close()  # 如果连接成功，立即关闭连接
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    # 使用线程运行WebSocket
    ws_thread = threading.Thread(target=run_ws, args=(ws,))
    ws_thread.daemon = True
    ws_thread.start()
    root.mainloop()
