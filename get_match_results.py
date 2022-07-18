import time
import requests
import psycopg2
from unidecode import unidecode
import json
import mwclient
from league_mapper import *
import os
from dotenv import load_dotenv
load_dotenv()

def check_if_duplicate_game(game_date, game_count, blue_team, red_team):
    for game in match_data:
        if game[0] == game_date and game[1] == game_count and game[2] == blue_team and game[3] == red_team:
            return True
    return False

def check_if_match_exists(game_date, game_count, blue_team, red_team):
    for game in matches_played:
        db_date = game['game_date'].split('T')[0].replace("-", "/")
        game_number = str(game['game_count'])
        team_one = (game['blue_team'])
        team_two = (game['red_team'])

        if (db_date == game_date) and ((team_one == blue_team) or (team_two == blue_team)) and (game_number == game_count) and ((team_two == red_team) or (team_one == red_team)):
            return True
    return False

list_of_leagues_to_scrape = [
    'LCK/2022 Season/Summer Season', # LCK 1
    'LEC/2022 Season/Summer Season', # LEC 2 
    'LVP SuperLiga/2022 Season/Summer Season', # LVP 3 
    'LCO/2022 Season/Split 2', # LCO (Oceania) 4 
    'LFL/2022 Season/Summer Season', # LFL 5 
    'PCS/2022 Season/Summer Season', # PCS 6 
    'LCS/2022 Season/Summer Season', # LCS 7 
    'NA Academy League/2022 Season/Summer Season',
    'LLA/2022 Season/Closing Season', # LLA 9 
    'Ultraliga/Season 8', # Ultraliga 10 
    # 'LPL/2022 Season/Summer Season', # LPL 11 Does not work as it uses https://lpl.qq.com/
    'LJL/2022 Season/Summer Season', # LJL 12 
    'TCL/2022 Season/Summer Season', # TCL 13 
    'VCS/2022 Season/Summer Season', # VCS 14
    'CBLOL/2022 Season/Split 2', # CBLOL 15 
]

response = requests.get("https://lol-betting.herokuapp.com/api/games")
matches_played = json.loads(response.text)

matches_to_post = []

site = mwclient.Site('lol.fandom.com', path='/')

for league_url in list_of_leagues_to_scrape:
    print("Scraping " + league_url)

    page_to_query = league_url
    response = site.api('cargoquery',
        limit = 'max',
        tables = 'MatchScheduleGame=MSG, MatchSchedule=MS, PostgameJsonMetadata=PJM',
        fields = 'MSG.RiotPlatformGameId, MS.DateTime_UTC, MSG.N_GameInMatch, MSG.Blue, MSG.Red, PJM.RiotVersion',
        where = r'MS.OverviewPage="%s"' % page_to_query,
        join_on = 'MSG.MatchId=MS.MatchId, MS.MatchId=PJM.MatchId',
        order_by = 'MS.DateTime_UTC DESC'
    )

    match_data = []

    for match in response["cargoquery"]:
        match = match["title"]
        if match["Blue"] and match["Red"] and match["RiotPlatformGameId"]:
            if not check_if_duplicate_game(match["DateTime UTC"].split(" ")[0], match["N GameInMatch"], unidecode(match["Blue"]), unidecode(match["Red"])):
                match_data.append([match["DateTime UTC"].split(" ")[0], match["N GameInMatch"], unidecode(match["Blue"]), unidecode(match["Red"]), "V5 data:" + match["RiotPlatformGameId"].replace("_", " ") + "/Timeline"])

    league = league_url.split("/")

    league = league[0]

    league_id = get_league_id(league)
    split_id = get_split_id(league)

    for match in match_data:        
        game_date = match[0].replace('-', '/')
        game_number = match[1]
        blue_team = unidecode(match[2])
        red_team = unidecode(match[3])

        if not check_if_match_exists(game_date, game_number, blue_team, red_team):
            blue_team_id = 100
            red_team_id = 200

            response = site.api('query',
                format = 'json',
                prop = 'revisions',
                rvprop = 'content',
                rvslots = 'main',
                titles = match[4]
            )

            pageId = ""

            for key in response["query"]["pages"].keys(): 
                pageId = key
                
            if "revisions" in response['query']['pages'][pageId].keys(): # Handle missing game history here
                data = response["query"]["pages"][pageId]["revisions"][0]["slots"]["main"]["*"]
                data_obj = json.loads(data)

                first_tower_killed_by_team = -1
                first_inhibitor_killed_by_team = -1
                first_dragon_killed_by_team = -1
                first_rift_herald_killed_by_team = -1
                first_baron_killed_by_team = -1
                first_blood_killed_by_team = -1
                blue_team_kill_count = 0
                red_team_kill_count = 0
                winning_team = -1
                losing_team = -1

                for event in data_obj["frames"]:
                    for specificEvent in event["events"]:
                        if ("monsterType" in specificEvent) and (specificEvent["monsterType"] == "DRAGON") and (first_dragon_killed_by_team == -1):
                            first_dragon_killed_by_team = specificEvent["killerTeamId"]
                        if ("monsterType" in specificEvent) and (specificEvent["monsterType"] == "RIFTHERALD") and (first_rift_herald_killed_by_team == -1):
                            first_rift_herald_killed_by_team = specificEvent["killerTeamId"]
                        if ("monsterType" in specificEvent) and (specificEvent["monsterType"] == "BARON_NASHOR") and (first_baron_killed_by_team == -1):
                            first_baron_killed_by_team = specificEvent["killerTeamId"]
                        if ("killType" in specificEvent) and (specificEvent["killType"] == "KILL_FIRST_BLOOD") and (first_blood_killed_by_team == -1):
                            if specificEvent["killerId"] > 5:
                                first_blood_killed_by_team = 200
                            else:
                                first_blood_killed_by_team = 100
                        if ("type" in specificEvent) and (specificEvent["type"] == "BUILDING_KILL"):
                            if ("towerType" in specificEvent) and (specificEvent["towerType"] == "OUTER_TURRET") and (first_tower_killed_by_team == -1):
                                if specificEvent["teamId"] == 100:
                                    first_tower_killed_by_team = 200
                                else:
                                    first_tower_killed_by_team = 100
                            if ("buildingType" in specificEvent) and (specificEvent["buildingType"] == "INHIBITOR_BUILDING") and (first_inhibitor_killed_by_team == -1):
                                if specificEvent["teamId"] == 100:
                                    first_inhibitor_killed_by_team = 200
                                else:
                                    first_inhibitor_killed_by_team = 100
                        if ("type" in specificEvent) and (specificEvent["type"] == "GAME_END"):
                            winning_team = specificEvent["winningTeam"]
                            if winning_team == 100:
                                losing_team = 200
                            else:
                                losing_team = 100
                        if ("type" in specificEvent) and (specificEvent["type"] == "CHAMPION_KILL"):
                            if specificEvent["killerId"] > 5:
                                red_team_kill_count = red_team_kill_count + 1
                            else:
                                blue_team_kill_count = blue_team_kill_count + 1

                if first_blood_killed_by_team == 100:
                    first_blood_killed_by_team = blue_team
                elif first_blood_killed_by_team == 200:
                    first_blood_killed_by_team = red_team
                else:
                    first_blood_killed_by_team = "-"

                if first_tower_killed_by_team == 100:
                    first_tower_killed_by_team = blue_team
                elif first_tower_killed_by_team == 200:
                    first_tower_killed_by_team = red_team
                else:
                    first_tower_killed_by_team = "-"

                if first_inhibitor_killed_by_team == 100:
                    first_inhibitor_killed_by_team = blue_team
                elif first_inhibitor_killed_by_team == 200:
                    first_inhibitor_killed_by_team = red_team
                else:
                    first_inhibitor_killed_by_team = "-"

                if first_dragon_killed_by_team == 100:
                    first_dragon_killed_by_team = blue_team
                elif first_dragon_killed_by_team == 200:
                    first_dragon_killed_by_team = red_team
                else:
                    first_dragon_killed_by_team = "-"

                if first_rift_herald_killed_by_team == 100:
                    first_rift_herald_killed_by_team = blue_team
                elif first_rift_herald_killed_by_team == 200:
                    first_rift_herald_killed_by_team = red_team
                else:
                    first_rift_herald_killed_by_team = "-"

                if first_baron_killed_by_team == 100:
                    first_baron_killed_by_team = blue_team
                elif first_baron_killed_by_team == 200:
                    first_baron_killed_by_team = red_team
                else:
                    first_baron_killed_by_team = "-"

                if winning_team == 100:
                    winning_team = blue_team
                elif winning_team == 200:
                    winning_team = red_team
                else:
                    winning_team = "-"

                if losing_team == 100:
                    losing_team = blue_team
                elif losing_team == 200:
                    losing_team = red_team
                else:
                    losing_team = "-"

                matches_to_post.append([league_id, split_id, game_date, game_number, blue_team, red_team, first_blood_killed_by_team, first_tower_killed_by_team, first_dragon_killed_by_team, first_inhibitor_killed_by_team, first_baron_killed_by_team, first_rift_herald_killed_by_team, blue_team_kill_count, red_team_kill_count, winning_team, losing_team])
            else:
                matches_to_post.append([league_id, split_id, game_date, game_number, blue_team, red_team, "-", "-", "-", "-", "-", "-", 0, 0, "-", "-"])

print('Finished scraping!')

for match_stats in matches_to_post:
     print("match_to_post: ", match_stats)

if len(matches_to_post) > 0:
    # Confirm if the user wants to post to the database or not
    print("Would you like to post the new data to the database (y/n)? ")
    post_data = input()

    if post_data == "y" or post_data == "Y":
        print('Posting to the database')

        env_var = os.environ
        db_user = env_var.get("db-user")
        db_password = env_var.get("db-password")
        db_host = env_var.get("db-host")
        db_port = env_var.get("db-port")
        db = env_var.get("db")

        conn = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db, sslmode='require')
        cur = conn.cursor()

        cur.execute("SELECT MAX(id) FROM games;")
        unique_id = cur.fetchone()

        if not all(unique_id):
            unique_id = 0
        else:
            unique_id = unique_id[0]

        print("unique_id is: ", unique_id)

        cur.execute("SELECT COUNT(*) FROM games")
        unique_id = cur.fetchone()
        unique_id = unique_id[0]

        for match_stats in matches_to_post:
            print("\nInsert into games: ", match_stats[:6])
            print("Insert into match_results: ", match_stats[6:])
            unique_id = unique_id+1
            cur.execute("INSERT INTO games VALUES (" + str(unique_id) +
                        " , %s, %s, %s, %s, %s, %s)", match_stats[:6])
            cur.execute("INSERT INTO match_results VALUES (" + str(unique_id) +
                        " , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", match_stats[6:])

        print("Files were committed to the database")
        conn.commit()

