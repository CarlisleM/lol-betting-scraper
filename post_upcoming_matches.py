import csv
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

print('Posting upcoming matches to the database')

env_var = os.environ
db_user = env_var.get("db-user")
db_password = env_var.get("db-password")
db_host = env_var.get("db-host")
db_port = env_var.get("db-port")
db = env_var.get("db")

conn = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db, sslmode='require')
cur = conn.cursor()

input_files = {
    'CBLOL Upcoming Games.csv',
    'LCK Upcoming Games.csv',
    'LCO Upcoming Games.csv',
    'LCS Upcoming Games.csv',
    'LEC Upcoming Games.csv',
    'LLA Upcoming Games.csv',
    'LPL Upcoming Games.csv',
    'LVP SuperLiga Upcoming Games.csv',
    'NA Academy League Upcoming Games.csv',
    'PCS Upcoming Games.csv',
    'TCL Upcoming Games.csv',
    'Ultraliga Upcoming Games.csv',
    'LFL Upcoming Games.csv',
    'LJL Upcoming Games.csv',
    'VCS Upcoming Games.csv',
}

cur.execute("DELETE FROM upcoming;")

for file in input_files:
    print("Adding upcoming matches from " + file + ' to the database')
    with open("./Upcoming Matches/" + file, 'r') as f:
        reader = csv.reader(f)
        for (index, row) in enumerate(reader):
            print(index)
            cur.execute(
                "INSERT INTO upcoming VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", row[:8])

print("Commiting files to the database")
conn.commit()
