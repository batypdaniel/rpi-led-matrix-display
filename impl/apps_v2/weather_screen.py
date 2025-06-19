import numpy as np, requests, math, time, threading
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO


class WeatherScreen:
    def __init__(self, config, modules):
        self.modules = modules

        self.little_font = ImageFont.truetype("fonts/tiny.otf", 5)
        self.big_font = ImageFont.truetype("fonts/tiny.otf", 10)

        self.current_icon_url = ""
        self.current_icon = None
        self.daily_icon_url = ""
        self.daily_icon = None

        self.canvas_width = 64
        self.canvas_height = 64
        self.text_color = (255, 255, 255)

        self.last_fetch_time = math.floor(time.time())
        self.fetch_interval = 1
        self.weather_module = self.modules['weather']

        self.response = None
        self.thread = threading.Thread(target=self.getCurrentWeatherAsync)
        self.thread.start()

    def getCurrentWeatherAsync(self):
        # delay spotify fetches
        time.sleep(3)
        while True:
            self.weather_module.get_weather_data()
            self.response = self.weather_module.weather_data
            time.sleep(15 * 60)

    def generate(self):
        return self.generateFrame(self.response)

    def generateFrame(self, response):
        if response is not None:

            current_temp, feels_like, current_condition, current_icon_url, \
                high, low, daily_condition, daily_icon_url, wind_speed, humidity = response['current_temp'], \
                                                                                    response['feels_like'], \
                                                                                    response['current_condition'], \
                                                                                    response['current_icon_url'], \
                                                                                    response['high'], \
                                                                                    response['low'], \
                                                                                    response['daily_condition'], \
                                                                                    response['daily_icon_url'], \
                                                                                    response['wind_speed'], \
                                                                                    response['humidity']

            if self.current_icon_url != current_icon_url:
                self.current_icon_url = current_icon_url
                response = requests.get(f"https://openweathermap.org/img/wn/{self.current_icon_url}@2x.png")
                img1 = Image.open(BytesIO(response.content))
                self.current_icon = img1.resize((32, 32), resample=3)

            if self.daily_icon_url != daily_icon_url:
                self.daily_icon_url = daily_icon_url
                response = requests.get(f"https://openweathermap.org/img/wn/{self.daily_icon_url}@2x.png")
                img2 = Image.open(BytesIO(response.content))
                self.daily_icon = img2.resize((20, 20), resample=3)

            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
            draw = ImageDraw.Draw(frame)

            # paste in logos
            frame.paste(self.current_icon, (33, 1))

            # Write Current Temp
            str_width = draw.textbbox((0, 0), current_temp, font=self.big_font)[2]
            draw.text((2, 10), current_temp, self.text_color, font=self.big_font)
            draw.text((3 + str_width, 7), "o", self.text_color, font=self.little_font)
            draw.text((8 + str_width, 10), "F", self.text_color, font=self.little_font)

            # Write Feels-Like
            draw.text((2, 22), "Feels " + feels_like, self.text_color, font=self.little_font)

            # Write Others
            draw.text((2, 35), "Today: " + daily_condition, self.text_color, font=self.little_font)
            str_width = draw.textbbox((0, 0), "H/L: " + high + "/" + low, font=self.little_font)[2]
            draw.text((2, 42), "H/L: " + high + "/" + low, self.text_color, font=self.little_font)
            draw.text((2 + str_width, 38), ".", self.text_color, font=self.little_font)
            draw.text((5 + str_width, 42), "F", self.text_color, font=self.little_font)

            draw.text((2, 54), "Humidity: " + humidity, self.text_color, font=self.little_font)

            return frame, True
        else:
            # not active
            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
            draw = ImageDraw.Draw(frame)

            self.current_icon_url = ''
            self.daily_icon_url = ''

            return frame, False


def drawPlayPause(draw, is_playing, color):
    x = 10
    y = -16
    if not is_playing:
        draw.line((x + 45, y + 19, x + 45, y + 25), fill=color)
        draw.line((x + 46, y + 20, x + 46, y + 24), fill=color)
        draw.line((x + 47, y + 20, x + 47, y + 24), fill=color)
        draw.line((x + 48, y + 21, x + 48, y + 23), fill=color)
        draw.line((x + 49, y + 21, x + 49, y + 23), fill=color)
        draw.line((x + 50, y + 22, x + 50, y + 22), fill=color)
    else:
        draw.line((x + 45, y + 19, x + 45, y + 25), fill=color)
        draw.line((x + 46, y + 19, x + 46, y + 25), fill=color)
        draw.line((x + 49, y + 19, x + 49, y + 25), fill=color)
        draw.line((x + 50, y + 19, x + 50, y + 25), fill=color)
