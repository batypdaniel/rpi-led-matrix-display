import numpy as np, requests, math, time, threading
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO


class EspnTicker:
    def __init__(self, config, modules):
        self.modules = modules

        self.little_font = ImageFont.truetype("fonts/tiny.otf", 5)
        self.big_font = ImageFont.truetype("fonts/tiny.otf", 10)

        self.canvas_width = 64
        self.canvas_height = 64
        self.text_color = (255, 255, 255)
        self.winner_color = (255, 255, 0)

        self.current_home_logo_url = ''
        self.current_away_logo_url = ''
        self.current_home_logo_img = None
        self.current_away_logo_img = None

        self.last_fetch_time = math.floor(time.time())
        self.fetch_interval = 1
        self.espn_module = self.modules['espn']

        self.response = None
        self.sport = None
        self.thread = threading.Thread(target=self.getCurrentGameAsync)
        self.thread.start()

    def getCurrentGameAsync(self):
        # delay spotify fetches
        time.sleep(3)
        while True:
            for sport in self.espn_module.sport_names:
                self.espn_module.get_sport_scoreboard(sport)
                self.sport = sport
                for i in range(len(self.espn_module.scoreboard[sport])):
                    self.response = self.espn_module.scoreboard[sport][i]
                    time.sleep(5)
                time.sleep(1)

    def generate(self):
        return self.generateFrame(self.response)

    def generateFrame(self, response):
        if response is not None:
            home_team, away_team, top_center, bottom_center, game_status = response['home_team'], \
                                                                            response['away_team'], \
                                                                            response['top_center'], \
                                                                            response['bottom_center'], \
                                                                            response['game_status']

            try:
                situation = response['situation']
                on_first = response['on_first']
                on_second = response['on_second']
                on_third = response['on_third']
            except:
                situation = ""

            if self.current_home_logo_url != home_team['logo_url']:
                self.current_home_logo_url = home_team['logo_url']
                response = requests.get(self.current_home_logo_url)
                img1 = Image.open(BytesIO(response.content))
                self.current_home_logo_img = img1.resize((26, 26), resample=3)

            if self.current_away_logo_url != away_team['logo_url']:
                self.current_away_logo_url = away_team['logo_url']
                response = requests.get(self.current_away_logo_url)
                img2 = Image.open(BytesIO(response.content))
                self.current_away_logo_img = img2.resize((26, 26), resample=3)

            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
            draw = ImageDraw.Draw(frame)

            # paste in logos
            if (self.current_home_logo_img is not None) & (self.current_away_logo_img is not None):
                frame.paste(self.current_away_logo_img, (4, 15))
                frame.paste(self.current_home_logo_img, (36, 15))

            if game_status == "STATUS_SCHEDULED":
                # Write Team Abbreviation
                str_width = draw.textbbox((0, 0), away_team['abbreviation'], font=self.big_font)[2]
                draw.text((16 - str_width // 2, 43), away_team['abbreviation'], self.text_color, font=self.big_font)
                str_width = draw.textbbox((0, 0), home_team['abbreviation'], font=self.big_font)[2]
                draw.text((49 - str_width // 2, 43), home_team['abbreviation'], self.text_color, font=self.big_font)

                # Write Team Score
                str_width = draw.textbbox((0, 0), away_team['score'], font=self.little_font)[2]
                draw.text((16 - str_width // 2, 55), away_team['score'], self.text_color, font=self.little_font)
                str_width = draw.textbbox((0, 0), home_team['score'], font=self.little_font)[2]
                draw.text((49 - str_width // 2, 55), home_team['score'], self.text_color, font=self.little_font)

                # Write Team Record
                str_width = draw.textbbox((0, 0), away_team['record'], font=self.little_font)[2]
                draw.text((16 - str_width // 2, 9), away_team['record'], self.text_color, font=self.little_font)
                str_width = draw.textbbox((0, 0), home_team['record'], font=self.little_font)[2]
                draw.text((49 - str_width // 2, 9), home_team['record'], self.text_color, font=self.little_font)

                # Write @ Between teams
                draw.text((30, 47), "@", self.text_color, font=self.little_font)

            elif game_status in ["STATUS_COMPLETED", "STATUS_FINAL"]:
                if int(away_team['score']) > int(home_team['score']):
                    away_color = self.winner_color
                    home_color = self.text_color
                else:
                    away_color = self.text_color
                    home_color = self.winner_color

                # Write Team Abbreviation
                str_width = draw.textbbox((0, 0), away_team['abbreviation'], font=self.little_font)[2]
                draw.text((16 - str_width // 2, 43), away_team['abbreviation'], away_color, font=self.little_font)
                str_width = draw.textbbox((0, 0), home_team['abbreviation'], font=self.little_font)[2]
                draw.text((49 - str_width // 2, 43), home_team['abbreviation'], home_color, font=self.little_font)

                # Write Team Score
                str_width = draw.textbbox((0, 0), away_team['score'], font=self.big_font)[2]
                draw.text((16 - str_width // 2, 50), away_team['score'], away_color, font=self.big_font)
                str_width = draw.textbbox((0, 0), home_team['score'], font=self.big_font)[2]
                draw.text((49 - str_width // 2, 50), home_team['score'], home_color, font=self.big_font)

                # Write Team Record
                str_width = draw.textbbox((0, 0), away_team['record'], font=self.little_font)[2]
                draw.text((16 - str_width // 2, 9), away_team['record'], away_color, font=self.little_font)
                str_width = draw.textbbox((0, 0), home_team['record'], font=self.little_font)[2]
                draw.text((49 - str_width // 2, 9), home_team['record'], home_color, font=self.little_font)

                # Write @ Between teams
                draw.text((30, 43), "@", self.text_color, font=self.little_font)

            else:
                # Write Team Abbreviation
                str_width = draw.textbbox((0, 0), away_team['abbreviation'], font=self.little_font)[2]
                draw.text((16 - str_width // 2, 43), away_team['abbreviation'], self.text_color, font=self.little_font)
                str_width = draw.textbbox((0, 0), home_team['abbreviation'], font=self.little_font)[2]
                draw.text((49 - str_width // 2, 43), home_team['abbreviation'], self.text_color, font=self.little_font)

                # Write Team Score
                str_width = draw.textbbox((0, 0), away_team['score'], font=self.big_font)[2]
                draw.text((16 - str_width // 2, 50), away_team['score'], self.text_color, font=self.big_font)
                str_width = draw.textbbox((0, 0), home_team['score'], font=self.big_font)[2]
                draw.text((49 - str_width // 2, 50), home_team['score'], self.text_color, font=self.big_font)

                try:
                    if situation != "":
                        # Write Situation
                        str_width = draw.textbbox((0, 0), situation, font=self.little_font)[2]
                        draw.text((28 - str_width // 2, 9), situation, self.text_color, font=self.little_font)
                        first_color = (0, 0, 255) if on_first else (150, 150, 150)
                        second_color = (0, 0, 255) if on_second else (150, 150, 150)
                        third_color = (0, 0, 255) if on_third else (150, 150, 150)
                        draw.rectangle([(30 - str_width // 2 + str_width, 12), (31 - str_width // 2 + str_width, 13)],
                                       fill=third_color)
                        draw.rectangle([(34 - str_width // 2 + str_width, 12), (35 - str_width // 2 + str_width, 13)],
                                       fill=first_color)
                        draw.rectangle([(32 - str_width // 2 + str_width, 9), (33 - str_width // 2 + str_width, 10)],
                                       fill=second_color)
                except:
                    # Write Situation
                    str_width = draw.textbbox((0, 0), situation, font=self.little_font)[2]
                    draw.text((32 - str_width // 2, 9), situation, self.text_color, font=self.little_font)

                # Write @ Between teams
                draw.text((30, 48), "@", self.text_color, font=self.little_font)

            # Write Top Center
            str_width = draw.textbbox((0, 1), top_center, font=self.little_font)[2]
            if game_status == "STATUS_COMPLETED":
                draw.text((32 - str_width // 2, 1), top_center, self.winner_color, font=self.little_font)
            else:
                draw.text((32 - str_width // 2, 1), top_center, self.text_color, font=self.little_font)

            return frame, True
        else:
            # not active
            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
            draw = ImageDraw.Draw(frame)

            self.current_home_logo_url = ''
            self.current_away_logo_url = ''

            return None, False


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
