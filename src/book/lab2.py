"""
This file compiles the code in Web Browser Engineering,
up to and including Chapter 2 (Drawing to the Screen),
without exercises.
"""

import wbetools
import socket
import ssl
import tkinter
from lab1 import URL

def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
        wbetools.record("lex", text)
    return text

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18

SCROLL_STEP = 100

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
        wbetools.record("layout", display_list)
    return display_list

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )

        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)

        self.window.bind("<MouseWheel>", self.handle_mouse_whell)
        self.window.bind("<Configure>", self.handle_window_config_change)

    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()


    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            wbetools.record("draw")
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def handle_mouse_whell(self, e):
        self.scroll -= e.delta
        self.draw()
    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def handle_window_config_change(self, e):
        print("lab2 assignment3 未实现！")
if __name__ == "__main__":
    """import sys

    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()"""

    Browser().load(URL("https://browser.engineering/examples/xiyouji.html"))
    tkinter.mainloop()
