import csv
import re
import time
import pandas as pd
from unidecode import unidecode
from bs4 import BeautifulSoup
from selenium import webdriver
from league_mapper import *
import os
from dotenv import load_dotenv
load_dotenv()

env_var = os.environ
chrome_driver = env_var.get("chrome-driver")

def get_page_source(link):
    driver.get(link)
    show_all = driver.find_element_by_xpath(
        '//*[@id="matchlist-show-all"]')
    show_all.click()
    time.sleep(5) # Probably not needed at all or can be greatly reduced
    return driver.page_source

#### THIS SECTION LOGS US IN TO THE LEAGUE OF LEGENDS WEBSITE ###

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-extensions')
driver = webdriver.Chrome(executable_path=chrome_driver, options=options)
driver.implicitly_wait(10)  # not sure if needed

############ THIS SECTION GATHERS ALL THE MATCH DATA ############

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
]

id = 1

for league_url in list_of_leagues_to_scrape:
    league = league_url.split("/")
    league = league[4].replace("_", " ")
    league_id = get_league_id(league)

    print('Scraping ' + league + ' main page')

    page_source = get_page_source(league_url)
    soup = BeautifulSoup(page_source, 'html.parser')

    teams = []
    teams_table = soup.find(attrs={"class": ["wikitable2 standings"]})
    rows = teams_table.findChildren(['tr'])

    for row in rows[1:len(rows)]:
        team_info_row = row.find(attrs={"class": ["popup-button-pretty"]})
        if team_info_row != None:
            split = re.split("team=|display=", str(team_info_row))
            team_name = split[1][:-1]
            team_abbreviation = split[2].split(" ")[0]
            teams.append([team_name, team_abbreviation])

    tbdcount = 0
    current_match_index = 0

    # Create a csv file to store upcoming matches
    tbd_outfile = "./Upcoming Matches/" + league + " Upcoming Games.csv"
    tbd_outfile = open(tbd_outfile, "w", newline='')
    tbd_writer = csv.writer(tbd_outfile)

    # Get list of matches for entire split (dates, teams and score)
    for week in range(1, 22): 
        print('league: ' + league + ', week: ' + str(week))

        match_counter = 0

        class_string_1 = 'ml-allw ml-w' + str(week) + ' ml-row'
        class_string_2 = 'ml-allw ml-w' + str(week) + ' ml-row matchlist-newday'

        games = soup.find_all(
            attrs={"class": [class_string_1, class_string_2]})

        if (len(games) > 0):
            final_match = games[len(games)-1]
            final_match = (final_match.text).split()

            final_match_t1 = final_match[0]
            final_match_t2 = final_match[4]

            for idx, character in enumerate(final_match_t1):
                for team in teams:
                    if team[1] in final_match_t1[-idx:]:
                        most_recent_game_t1 = team[1]

            for idx, character in enumerate(final_match_t2):
                for team in teams:
                    if team[1] in final_match_t2[-idx:]:
                        most_recent_game_t2 = team[1]
            
        number_of_games_played = len(games)
        number_of_games_in_week = int((len(soup.select('.ml-w' + str(week) + ' .ml-team')))/2)

        if number_of_games_in_week == number_of_games_played:
            current_match_index += number_of_games_in_week

        if (number_of_games_in_week > 0):
            if (number_of_games_played == 0) or (number_of_games_played != number_of_games_in_week):
                date_class_1 = 'ml-allw ml-w' + str(week) + ' ml-row ml-row-tbd'
                date_class_2 = 'ml-allw ml-w' + str(week) + ' ml-row ml-row-tbd matchlist-newday'
                date_class_3 = 'ml-allw ml-w' + str(week) + ' ml-row ml-row-tbd matchlist-flex'
                date_class_4 = 'ml-allw ml-w' + str(week) + ' ml-row-tbd matchlist-newday matchlist-flex'
                date_class_5 = 'ml-allw ml-w' + str(week) + ' ml-row ml-row-tbd matchlist-newday matchlist-flex'

                toggle_number = 1
                length_counter = len(soup.select('.ml-w' + str(week) + '.ofl-toggler-' + str(toggle_number) + '-all span'))

                while (length_counter == 0):
                    toggle_number += 1
                    length_counter = len(soup.select('.ml-w' + str(week) + '.ofl-toggler-' + str(toggle_number) + '-all span'))

                date_teams_class = '.matchlist-tab-wrapper:nth-child(' + str(week) + ') , .team , .ml-w' + str(week) + '.ofl-toggler-' + str(toggle_number) + '-all span'

                match_time_class = 'ofl-toggle-' + \
                    str(toggle_number) + '-2 ofl-toggler-' + \
                    str(toggle_number) + '-all'
                all_match_time = soup.find_all(
                    attrs={"class": match_time_class})

                if number_of_games_played == 0:
                    match_times = all_match_time[current_match_index:current_match_index+number_of_games_in_week]
                else:
                    match_times = all_match_time[current_match_index + number_of_games_played:current_match_index+number_of_games_in_week]

                current_match_index += number_of_games_in_week

                tbdgames = soup.find_all(
                    attrs={"class": [date_class_1, date_class_2]})

                if (len(tbdgames) == 0):
                    tbdgames = soup.find_all(attrs={"class": [date_class_1, date_class_2, date_class_3, date_class_4, date_class_5]})

                tbd_teams_dates = soup.select(date_teams_class)

                date_team_vs = []

                for game in tbdgames:
                    # print("\ngame:", game)
                    tbd_team_1 = ""
                    tbd_team_2 = ""

                    split = re.split("data-date=", str(game))
                    # print("split: ", split)
                    match_date = split[1][1:11]
                    match_day = (pd.Timestamp(match_date)).day_name()[0:3]
                    tbd_team_names = game.text
                    for idx, character in enumerate(tbd_team_names):
                        if tbd_team_1 == "" and idx > 0:
                            for team in teams:
                                if team[1] in tbd_team_names[:idx]:
                                    tbd_team_1 = team[0]
                    for idx, character in enumerate(tbd_team_names):
                        if tbd_team_2 == "" and idx > 0:
                            for team in teams:
                                if team[1] in tbd_team_names[-idx:]:
                                    tbd_team_2 = team[0]

                    date_team_vs.append(id) # Add the id of the match
                    date_team_vs.append(str(week)) # Add the week of the match
                    date_team_vs.append(league_id) # Add what league the match is from
                    date_team_vs.append(match_day) # Add the date of the match
                    date_team_vs.append(match_date) # Add the day of the match
                    date_team_vs.append(match_times[match_counter].text) # Add the time of the match
                    date_team_vs.append(unidecode(tbd_team_1))  # Add team 1
                    date_team_vs.append(unidecode(tbd_team_2))  # Add team 2
                    tbd_writer.writerows([date_team_vs])

                    match_counter += 1
                    id += 1
                    date_team_vs = []

print('Finished getting upcoming matches!')

# Close the browser
driver.close()
driver.quit()
