# -*- encoding: utf-8 -*-
'''
@File    :   player.py
@Time    :   2020/06/13 22:20:34
@Author  :   Fan Lingjie 
@Version :   1.0
@Contact :   fanlingjie@laiye.com
'''

import tkinter as tk
from PIL import ImageTk, Image  
import time
import requests
from bs4 import BeautifulSoup
import threading
import os

def parse_page(url):
    """
        解析网页
        
        @param 
            url: 网页URL
        @return 
            title: 章节标题
            content: 章节内容
            next_url: 下一章URL
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.find('h1').get_text()
    p_list = soup.select('div#neirong p')
    content = [p.get_text().strip() for p in p_list]
    urls = soup.select("a#BookNext")
    if urls:
        next_url = urls[0]['href']
    else:
        next_url = None
    return title, content, next_url


def read_text(text, root):
    """
        朗读章节标题
    """
    # engine.say(title)
    # engine.runAndWait()
    
    # MacOS有线程问题,改用系统方法
    # https://github.com/nateshmbhat/pyttsx3/issues/8
    os.system(f"say {text}")
    while True:
        if root.stopped:
            break
        time.sleep(1)
        if not root.paused:
            break
        

class Player(object):
    def __init__(self, root, filename, **kwargs):
        self.root = root
        self.filename = filename
        self.canvas = tk.Canvas(root, width=200, height=200)
        self.canvas.pack()

        self.update = self.draw().__next__
        self.timer = self.root.after(100, self.update)

        self.btn_text = tk.StringVar()
        self.btn_text.set("暂停")
        self.paused = False
        self.stopped = False
        self.btn_play = tk.Button(root, height=2, width=6,
                                        padx=3, pady=3,
                                        textvariable=self.btn_text, 
                                        command=self.btn_handler)
        self.btn_play.pack()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.stopped = True
        print("on_closing...")
        self.root.destroy()

    def btn_handler(self):
        text = self.btn_text.get()
        if text == "继续":
            self.paused = False
            self.btn_text.set("暂停")
        else:
            self.paused = True
            self.btn_text.set("继续")
            

    def draw(self):
        image = Image.open(self.filename)
        angle = 0
        while True:
            tkimage = ImageTk.PhotoImage(image.rotate(angle))
            canvas_obj = self.canvas.create_image(
                100, 100, image=tkimage)
            self.root.after_idle(self.update)
            yield
            self.canvas.delete(canvas_obj)
            if not self.paused:
                angle -= 10
            angle %= 360
            time.sleep(0.2)
            


class PlayThread(threading.Thread):
    def __init__(self, root, url):
        self.root = root
        self.url = url
        self.thread = threading.Thread(target=self.play)
        self.thread.start()

    def play(self):
        while True:
            print("start....")
            title, content, next_url = parse_page(self.url)
            read_text(title, self.root)
            for c in content:
                # 现在以段落为单位进行暂停
                print(self.root.stopped)
                if self.root.stopped:
                    break
                read_text(c, self.root)
            if next_url:
                self.url = next_url
            else:
                break
            if self.root.stopped:
                break

root = tk.Tk()
root.title("斗破苍穹")
url = "https://www.51shucheng.net/wangluo/doupocangqiong/23716.html"
app = Player(root, 'player_bg.png')
playthread = PlayThread(app, url)
root.mainloop()
