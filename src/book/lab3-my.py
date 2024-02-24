"""
This file compiles the code in Web Browser Engineering,
up to and including Chapter 3 (Formatting Text),
without exercises.
"""
import string

import wbetools
import socket
import ssl
import tkinter
import tkinter.font
from lab1 import URL
from lab2 import WIDTH, HEIGHT, HSTEP, VSTEP, SCROLL_STEP, Browser
from src.book import lab2


class Token:
    def __init__(self, literal: str):
        pass

    def __repr__(self):
        pass


class Text(Token):
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return f"Text('{self.text}')"


class Tag(Token):
    def __init__(self, tag: str):
        self.tag = tag

    def __repr__(self):
        return f"Tag('{self}')"


def lex(body: str):
    res = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer: res.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            if buffer: res.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer: res.append(Text(buffer))
    return res


FONTS = {}


def get_font(size, weight, slant):
    key = (size, weight, slant)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=slant)
        lable = tkinter.Label(font=font)
        FONTS[key] = (font, lable)
    return FONTS[key][0]


class Layout:
    def __init__(self, tokens):
        self.tokens = tokens
        self.display_list = []

        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        self.line = []
        for token in tokens:
            self.token(token)

    def my_split(self, text):
        text = text.replace("\n", "")

        res = []
        word = ""
        for c in text:
            word += c
            if c in string.ascii_letters and (c not in [",", ".", "?", " "]):
                continue

            '''if (c in string.ascii_letters) and (c not in [",", ".", "?", "，", "。", "？", "、", " "]):
                continue'''
            # push as a word
            res.append(word)
            word = ""
        return res
    def token(self, token: Token):
        if isinstance(token, Text):
            for word in self.my_split(token.text):
                self.word(word)
        elif isinstance(token, Tag):
            if token.tag == "i":
                self.style = "italic"
            elif token.tag == "/i":
                self.style = "roman"
            elif token.tag == "b":
                self.weight = "bold"
            elif token.tag == "/b":
                self.weight = "normal"
            elif token.tag == "small":
                self.size -= 2
            elif token.tag == "/small":
                self.size += 2
            elif token.tag == "big":
                self.size += 4
            elif token.tag == "/big":
                self.size -= 4
            elif token.tag == "br":
                self.flush()
            elif token.tag == "/p":
                self.flush()
                self.cursor_y += VSTEP

    def word(self, word: str):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for _, _, font in self.line]
        max_ascent = max([font.metrics("ascent") for _, _, font in self.line])
        h_line_step = 1.25 * max_ascent
        baseline = self.cursor_y + h_line_step
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([font.metrics("descent") for _, _, font in self.line])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []


@wbetools.patch(Browser)
class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        self.display_list = []
        self.scroll = 0

        self.window.bind("<Down>", self.scrolldown)

        self.window.bind("<MouseWheel>", self.handle_mouse_wheel)
        self.window.bind("<Configure>", self.handle_window_config_change)

    def load(self, url):
        body = url.request()
        tokens = lex(body)
        self.display_list = Layout(tokens).display_list
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c, font in self.display_list:
            wbetools.record("draw")
            if y > self.scroll + HEIGHT: continue
            if y + font.metrics("linespace") < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c, font=font, anchor="nw")

    def handle_mouse_wheel(self, e):
        self.scroll -= e.delta
        self.draw()

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def handle_window_config_change(self, e):
        lab2.WIDTH = self.window.winfo_screenwidth()
        self.draw()
        print("lab2 assignment3 未实现！")


if __name__ == "__main__":
    """import sys

    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()"""

    # Browser().load(URL("https://browser.engineering/text.html"))
    Browser().load(URL("https://browser.engineering/examples/example3-sizes.html"))

    tkinter.mainloop()
