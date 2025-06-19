import requests
import json

class WeatherModule:
    def __init__(self):
        self.weather_data = None

    def get_weather_data(self):
        response = requests.get("https://api.openweathermap.org/data/3.0/onecall?lat=35.149&lon=-90.0516&exclude=minutely,hourly&units=imperial&appid=04b5263ef11855c05e12f80579c1813d")

        if response.ok:
            data = response.json()
        else:
            self.weather_data = None
            return

        vals = {}

        vals['current_temp'] = str(int(data['current']['temp']))
        vals['feels_like'] = str(int(data['current']['feels_like']))
        vals['current_condition'] = data['current']['weather'][0]['main']
        vals['current_icon_url'] = data['current']['weather'][0]['icon']
        vals['high'] = str(int(data['daily'][0]['temp']['max']))
        vals['low'] = str(int(data['daily'][0]['temp']['min']))
        vals['daily_condition'] = data['daily'][0]['weather'][0]['main']
        vals['daily_icon_url'] = data['daily'][0]['weather'][0]['icon']
        vals['wind_speed'] = str(int(data['current']['wind_speed'])) + "mph"
        vals['humidity'] = str(int(data['current']['humidity'])) + "%"

        self.weather_data = vals





