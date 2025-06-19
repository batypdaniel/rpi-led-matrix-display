import numpy as np, requests, math, time, threading
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

class TimeScreen:
    def __init__(self, config, modules, fullscreen):
        self.modules = modules

        self.date_font = ImageFont.truetype("fonts/tiny.otf", 5)
        self.time_font = ImageFont.truetype("fonts/tiny.otf", 10)

        self.canvas_width = 64
        self.canvas_height = 64
        self.date_color = (255,255,255)
        self.time_color = (255,255,255)

        self.full_screen_always = fullscreen

        self.is_playing = False

        self.last_fetch_time = math.floor(time.time())
        self.fetch_interval = 1

        self.response = None
        self.thread = threading.Thread(target=self.getDateAndTime)
        self.thread.start()

    def getDateAndTime(self):
        # delay time calculations
        time.sleep(1)
        while True:
            current_dt = datetime.now()
            self.response = {'date_string': current_dt.strftime('%a %b %d %Y'), 'time_string': current_dt.strftime('%I:%M %p')}
            time.sleep(1)

    def generate(self):
        return self.generateFrame(self.response)

    def generateFrame(self, response):
        if response is not None:
            date_string, time_string = response['date_string'], response['time_string']

            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
            draw = ImageDraw.Draw(frame)

            _, _, date_width, date_height = draw.textbbox((0, 0), date_string, font=self.date_font)
            _, _, time_width, time_height = draw.textbbox((0, 0), time_string, font=self.time_font)

            text_gap = 2

            draw.text(((self.canvas_width - time_width) // 2,
                       (self.canvas_height - (time_height + text_gap + date_height)) // 2), time_string, font=self.time_font)
            draw.text(((self.canvas_width - date_width) // 2,
                       (self.canvas_height - (time_height + text_gap + date_height)) // 2 + text_gap + time_height), date_string, font=self.date_font)

            return (frame, True)
        else:
            return (None, self.is_playing)
