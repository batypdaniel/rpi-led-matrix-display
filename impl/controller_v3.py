import os, inspect, sys, math, time, configparser, argparse, warnings
from PIL import Image
import threading
from display_state import display_state

from apps_v2 import spotify_player
from modules import spotify_module
from apps_v2 import time_player
from apps_v2 import text_screen
from apps_v2 import espn_ticker
from apps_v2 import weather_screen
from modules import weather_module
from modules import espn_api_module
from web_interface import app

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


def main():
    canvas_width = 64
    canvas_height = 64

    # get arguments
    parser = argparse.ArgumentParser(
                    prog = 'RpiSpotifyMatrixDisplay',
                    description = 'Displays album art of currently playing song on an LED matrix')

    parser.add_argument('-e', '--emulated', action='store_true', help='Run in a matrix emulator')
    args = parser.parse_args()

    is_emulated = args.emulated

    # switch matrix library import if emulated
    if is_emulated:
        from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    else:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions

    # get config
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    sys.path.append(currentdir+"/rpi-rgb-led-matrix/bindings/python")

    config = configparser.ConfigParser()
    parsed_configs = config.read('../config.ini')

    if len(parsed_configs) == 0:
        print("no config file found")
        sys.exit()

    # connect to Spotify and create display image
    modules = { 'spotify': spotify_module.SpotifyModule(config),
                'espn': espn_api_module.EspnApiModule(),
                'weather': weather_module.WeatherModule()}
    app_list = { "Spotify (With Track/Artist Info)": spotify_player.SpotifyScreen(config, modules, False),
                 "Spotify (Full-Screen Album Art)": spotify_player.SpotifyScreen(config, modules, True),
                 "Time": time_player.TimeScreen(config, modules, True),
                 "ESPN Ticker": espn_ticker.EspnTicker(config, modules),
                 "Weather": weather_screen.WeatherScreen(config, modules),
                 "Custom Text": text_screen.TextScreen(config, display_state, True) }

    # setup matrix
    options = RGBMatrixOptions()
    options.hardware_mapping = config.get('Matrix', 'hardware_mapping', fallback='regular')
    options.rows = canvas_width
    options.cols = canvas_height
    options.brightness = 100 if is_emulated else config.getint('Matrix', 'brightness', fallback=100)
    options.gpio_slowdown = config.getint('Matrix', 'gpio_slowdown', fallback=1)
    options.limit_refresh_rate_hz = config.getint('Matrix', 'limit_refresh_rate_hz', fallback=0)
    options.drop_privileges = False
    matrix = RGBMatrix(options = options)

    shutdown_delay = config.getint('Matrix', 'shutdown_delay', fallback=600)
    black_screen = Image.new("RGB", (canvas_width, canvas_height), (0,0,0))
    last_active_time = math.floor(time.time())

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # generate image
    while(True):
        idx = display_state.current_app_label
        frame, is_playing = app_list[idx].generate()
        current_time = math.floor(time.time())

        if frame is not None:
            if is_playing:
                last_active_time = math.floor(time.time())
            elif current_time - last_active_time >= shutdown_delay:
                frame = black_screen
        else:
            frame = black_screen

        matrix.SetImage(frame)
        time.sleep(0.08)


if __name__ == '__main__':
    try:
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        main()
    except KeyboardInterrupt:
        print('Interrupted with Ctrl-C')
        sys.exit(0)
