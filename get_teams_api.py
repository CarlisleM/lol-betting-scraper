import psycopg2
from unidecode import unidecode
import mwclient
from league_mapper import *
import os
from dotenv import load_dotenv
load_dotenv()

def check_if_duplicate_team(check_team):
    for team in team_data:
        if team[1] == check_team:
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
    'LPL/2022 Season/Summer Season', # LPL 11
    'LJL/2022 Season/Summer Season', # LJL 12 
    'TCL/2022 Season/Summer Season', # TCL 13 
    'VCS/2022 Season/Summer Season', # VCS 14
    'CBLOL/2022 Season/Split 2', # CBLOL 15 
]

team_data = []

site = mwclient.Site('lol.fandom.com', path='/')

unique_team_id = 149 # was 0

for league_url in list_of_leagues_to_scrape:
    print("Scraping " + league_url)

    league = league_url.split("/")
    league = league[0]
    league_id = get_league_id(league)

    page_to_query = league_url
    response = site.api('cargoquery',
        limit = 'max',
        tables = 'MatchScheduleGame = MSG, MatchSchedule = MS',
        fields = 'MSG.Blue, MSG.Red',
        where = r'MS.OverviewPage = "%s"' % page_to_query,
        join_on = 'MSG.MatchId = MS.MatchId'
    )

    for match in response["cargoquery"]:
        match = match["title"]
        if match["Blue"] and match["Red"]:
            blueTeam = unidecode(match["Blue"])
            redTeam = unidecode(match["Red"])

            if not check_if_duplicate_team(blueTeam):
                team_data.append([unique_team_id, blueTeam, league_id])
                unique_team_id = unique_team_id + 1

            if not check_if_duplicate_team(redTeam):
                team_data.append([unique_team_id, redTeam, league_id])
                unique_team_id = unique_team_id + 1
    
print('Finished getting teams!')

for team in team_data:
    print("INSERT INTO teams VALUES (%s, %s, %s)", team[:3])

if len(team_data) > 0:
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

        for team in team_data:
            print("team_id: " + str(team[0]) + ", team: " + str(team[1]) + ", league: " + str(team[2]))
            cur.execute("INSERT INTO teams VALUES (%s, %s, %s)", team[:3])

        print("Files were committed to the database")
        conn.commit()

