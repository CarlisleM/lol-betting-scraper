import re
import time
import psycopg2
from unidecode import unidecode
from bs4 import BeautifulSoup
from selenium import webdriver
from league_mapper import *
import os
from dotenv import load_dotenv
load_dotenv()

def get_page_source(link):
    driver.get(link)
    return driver.page_source

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-extensions')
driver = webdriver.Chrome(executable_path='/Users/Carlisle/Desktop/Projects/chromedriver.exe', options=options)
#driver_location = str(sys.argv[1])
#driver = webdriver.Chrome(executable_path=driver_location, options=options)
driver.implicitly_wait(10)  # not sure if needed

list_of_leagues_to_scrape = [
    # 2022
    'https://lol.fandom.com/wiki/LCK/2022_Season/Summer_Season', # LCK 1 
    'https://lol.fandom.com/wiki/LEC/2022_Season/Summer_Season', # LEC 2 
    'https://lol.fandom.com/wiki/LVP_SuperLiga/2022_Season/Summer_Season', # LVP 3
    'https://lol.fandom.com/wiki/LCO/2022_Season/Split_2', # LCO (Oceania) 4
    'https://lol.fandom.com/wiki/LFL/2022_Season/Summer_Season', # LFL 5 
    'https://lol.fandom.com/wiki/PCS/2022_Season/Summer_Season', # PCS 6
    'https://lol.fandom.com/wiki/LCS/2022_Season/Summer_Season', # LCS 7 
    'https://lol.fandom.com/wiki/NA_Academy_League/2022_Season/Summer_Season', # NA Academy 8
    'https://lol.fandom.com/wiki/LLA/2022_Season/Closing_Season', # LLA 9 
    'https://lol.fandom.com/wiki/Ultraliga/Season_8', # Ultraliga 10
    'https://lol.fandom.com/wiki/LPL/2022_Season/Summer_Season', # LPL 11 
    'https://lol.fandom.com/wiki/LJL/2022_Season/Summer_Season', # LJL 12
    'https://lol.fandom.com/wiki/TCL/2022_Season/Summer_Season', # TCL 13
    'https://lol.fandom.com/wiki/VCS/2022_Season/Summer_Season', # VCS 14 
    'https://lol.fandom.com/wiki/CBLOL/2022_Season/Split_2', # CBLOL 15
    'https://lol.fandom.com/wiki/LCK_CL/2022_Season/Summer_Season', # LCK CL 16
    'https://lol.fandom.com/wiki/LPLOL/2022_Season/Summer_Season', # LPLOL 17 
    'https://lol.fandom.com/wiki/NLC/2022_Season/Summer_Season', # NLC 18
    'https://lol.fandom.com/wiki/Esports_Balkan_League/2022_Season/Summer_Split', # Esports Balkan League 19
    'https://lol.fandom.com/wiki/Hitpoint_Masters/2022_Season/Summer_Season', # Hitpoint Masters 20 
    'https://lol.fandom.com/wiki/Prime_League_1st_Division/2022_Season/Summer_Season', # Prime League 21 
    'https://lol.fandom.com/wiki/Turkey_Academy_League/2022_Season/Summer_Season', # Turkey Academy League 22 
    'https://lol.fandom.com/wiki/Elite_Series/2022_Season/Summer_Split', # Elite Series 23 
]

team_id = 1
teams = []

for league_url in list_of_leagues_to_scrape:
    league = league_url.split("/")
    league = league[4].replace("_", " ")
    league_id = get_league_id(league)

    print('Scraping ' + league)

    page_source = get_page_source(league_url)
    soup = BeautifulSoup(page_source, 'html.parser')

    teams_table = soup.find(attrs={"class": ["wikitable2 standings"]})
    rows = teams_table.findChildren(['tr'])

    for row in rows[1:len(rows)]:
        team_info_row = row.find(attrs={"class": ["popup-button-pretty"]})
        if team_info_row != None:
            split = re.split("team=|display=", str(team_info_row))
            team_name = split[1][:-1]
            team_abbreviation = split[2].split(" ")[0]
            teams.append([team_id, unidecode(team_name), unidecode(team_abbreviation), league_id])
            team_id = team_id + 1

print('Finished getting upcoming matches!')

for team in teams:
    print("team:", team)

if len(teams) > 0:
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

        for team in teams:
            print("team_id: " + str(team[0]) + ", team_name: " + str(team[1]) + ", team_abbreviation: " + str(team[2]) + ", league: " + str(team[3]))
            cur.execute("INSERT INTO teams VALUES (%s, %s, %s, %s)", team[:4])

        print("Files were committed to the database")
        conn.commit()

# Close the browser
driver.close()
driver.quit()
