import requests
import json

class EspnApiModule:
    def __init__(self):
        self.sports = {
            #"NFL": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
            "NBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
            #"NCAAF": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
            #"NCAAM": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard",
            "MLB": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
            #"Fantasy NFL": {},
            #"Fantasy NBA": {}
        }
        self.sport_names = list(self.sports.keys())
        self.scoreboard = {}

    def get_scoreboard_data(self):
        for sport in self.sport_names:
            self.get_sport_scoreboard(sport)

    def get_sport_scoreboard(self, sport):
        headers = {'Accept': 'application/json'}
        response = requests.get(self.sports[sport], headers=headers)

        if response.ok:
            data = response.json()
        else:
            self.scoreboard[sport] = []

        if not self.is_league_active(data):
            self.scoreboard[sport] = []
        else:
            ticker_values = []
            for event in data['events']:
                ticker_values.append(self.set_ticker_values(event))
            self.scoreboard[sport] = ticker_values

    def is_league_active(self, response_data):
        try:
            current_league_year, current_league_type = response_data['leagues'][0]['season']['year'], \
                                                        response_data['leagues'][0]['season']['type']['type']
            scoreboard_league_year, scoreboard_league_type = response_data['season']['year'], \
                                                             response_data['season']['type']

            return (current_league_year == scoreboard_league_year) & (current_league_type == scoreboard_league_type)
        except:
            return False

    def set_ticker_values(self, event_data):
        vals = {}
        game_status = event_data['competitions'][0]['status']['type']['name']
        vals['game_status'] = game_status

        teams_data = event_data['competitions'][0]['competitors']
        home_team = [team for team in teams_data if team['homeAway'] == "home"][0]
        away_team = [team for team in teams_data if team['homeAway'] == "away"][0]

        vals['home_team'] = {}
        vals['home_team']['logo_url'] = home_team['team']['logo']
        vals['home_team']['abbreviation'] = home_team['team']['abbreviation']
        try:
            vals['home_team']['record'] = home_team['records'][0]['summary']
        except:
            vals['home_team']['record'] = "0-0"

        vals['away_team'] = {}
        vals['away_team']['logo_url'] = away_team['team']['logo']
        vals['away_team']['abbreviation'] = away_team['team']['abbreviation']
        try:
            vals['away_team']['record'] = away_team['records'][0]['summary']
        except:
            vals['away_team']['record'] = "0-0"

        if game_status == "STATUS_SCHEDULED":
            vals['top_center'] = event_data['competitions'][0]['status']['type']['shortDetail'].replace(" - ", " ")
            if event_data['competitions'][0]['odds'][0]['homeTeamOdds']['favorite']:
                vals['home_team']['score'], vals['away_team']['score'] = \
                    str(event_data['competitions'][0]['odds'][0]['spread'] if event_data['competitions'][0]['odds'][0]['spread'] != 0 else "PK"), \
                    str(event_data['competitions'][0]['odds'][0]['overUnder'])
            else:
                vals['away_team']['score'], vals['home_team']['score'] = \
                    str(-1 * event_data['competitions'][0]['odds'][0]['spread'] if event_data['competitions'][0]['odds'][0]['spread'] != 0 else 'PK'), \
                    str(event_data['competitions'][0]['odds'][0]['overUnder'])
        elif game_status in ["STATUS_COMPLETED", "STATUS_FINAL"]:
            vals['top_center'] = "FT"
            vals['home_team']['score'] = str(home_team['score'])
            vals['away_team']['score'] = str(away_team['score'])
        else:
            periods = {2: "H", 3: "P", 4: "Q"}
            num_periods = event_data['competitions'][0]['format']['regulation']['periods']
            if num_periods != 9:
                vals['top_center'] = str(event_data['competitions'][0]['status']['period']) + \
                    ("OT" if event_data['competitions'][0]['status']['period'] > num_periods else str(periods[num_periods])) + \
                    " " + event_data['competitions'][0]['status']['displayClock']
                vals['situation'] = ""
            else:
                vals['top_center'] = event_data['competitions'][0]['status']['type']['shortDetail']
                try:
                    vals['situation'] = str(event_data['competitions'][0]['situation']['outs']) + " Out, " + str(event_data['competitions'][0]['situation']['strikes']) + "-" + str(event_data['competitions'][0]['situation']['strikes'])
                except:
                    vals['situation'] = ""
                try:
                    vals['on_first'] = event_data['competitions'][0]['situation']['onFirst']
                    vals['on_second'] = event_data['competitions'][0]['situation']['onSecond']
                    vals['on_third'] = event_data['competitions'][0]['situation']['onThird']
                except:
                    vals['on_first'] = False
                    vals['on_second'] = False
                    vals['on_third'] = False

            vals['home_team']['score'] = str(home_team['score'])
            vals['away_team']['score'] = str(away_team['score'])

        try:
            vals['bottom_center'] = event_data['competitions'][0]['notes'][0]['headline']
        except:
            vals['bottom_center'] = ""

        return vals



