import ctypes
import sys

import sdl2
import skia

import config
class Browser:
    def __init__(self):
        self.sdl_window = sdl2.SDL_CreateWindow(
            b"Raft",
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            config.window.width, config.window.height, sdl2.SDL_WINDOW_SHOWN
        )
        self.root_surface = skia.Surface.MakeRaster(
            skia.ImageInfo.Make(
                config.window.width, config.window.height,
                ct=skia.kRGBA_8888_ColorType,
                at=skia.kUnpremul_AlphaType
            ))

        if sdl2.SDL_BYTEORDER == sdl2.SDL_BIG_ENDIAN:
            self.RED_MASK = 0xff000000
            self.GREEN_MASK = 0x00ff0000
            self.BLUE_MASK = 0x0000ff00
            self.ALPHA_MASK = 0x000000ff
        else:
            self.RED_MASK = 0x000000ff
            self.GREEN_MASK = 0x0000ff00
            self.BLUE_MASK = 0x00ff0000
            self.ALPHA_MASK = 0xff000000

    def _update(self):
        skia_image = self.root_surface.makeImageSnapshot()
        skia_bytes = skia_image.tobytes()
        depth = 32  # Bits per pixel
        pitch = 4 * config.window.width  # Bytes per row
        sdl_surface = sdl2.SDL_CreateRGBSurfaceFrom(
            skia_bytes, config.window.width, config.window.height, depth, pitch,
            self.RED_MASK, self.GREEN_MASK, self.BLUE_MASK, self.ALPHA_MASK
        )
        # copy(swap) surface
        rect = sdl2.SDL_Rect(0, 0, config.window.width, config.window.height)
        window_surface = sdl2.SDL_GetWindowSurface(self.sdl_window)
        sdl2.SDL_BlitSurface(sdl_surface, rect, window_surface, rect)  # Actually does the copy
        sdl2.SDL_UpdateWindowSurface(self.sdl_window)
    def draw(self, canvas, offset):
        canvas = self.root_surface.getCanvas()


    def handle_quit(self):
        sdl2.SDL_DestroyWindow(self.sdl_window)

def mainloop(browser: Browser):
    event = sdl2.SDL_Event()
    while True:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                browser.handle_quit()
                sdl2.SDL_Quit()
                sys.exit()
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                browser.handle_click(event.button)
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_RETURN:
                    browser.handle_enter()
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    browser.handle_down()
            elif event.type == sdl2.SDL_TEXTINPUT:
                browser.handle_key(event.text.text.decode('utf8'))



if __name__ == "__main__":
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS)
    browser = Browser()
    mainloop(browser)
