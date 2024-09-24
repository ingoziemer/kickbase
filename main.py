from kickbase_api.kickbase import Kickbase
import pandas as pd
from datetime import datetime, timedelta
import os
import glob
from openpyxl.workbook import Workbook

pd.options.display.float_format = '{:,.2f}'.format
# gets user credentials from environment variables and logs in
USERNAME = os.environ["kickbase_user"]
PASSWORD = os.environ["kickbase_pw"]

kickbase = Kickbase()
user, league = kickbase.login(username=USERNAME, password=PASSWORD)

# choose league
DFS = league[0]

# get the players on your team and write their names and market value in a dataframe
user_players = kickbase.league_user_players(DFS, user=user)

player_names = []
player_market_values = []
day = []
avg_points = []
euro_per_point = []
for row in range(len(user_players)):
    player_names.append(user_players[row].last_name)
    player_market_values.append(user_players[row].market_value)
    day.append(datetime.today().strftime("%Y-%m-%d"))
    avg_points.append(user_players[row].average_points)
    if avg_points[row] == 0:
        euro_per_point.append(0)
    else:
        euro_per_point.append((player_market_values[row] / avg_points[row]))

data = [day, player_names, player_market_values, avg_points, euro_per_point]
df_today = pd.DataFrame(data).T

df_today.rename(columns={0: 'date', 1: 'name', 2: 'market_value', 3: 'avg_points', 4: '€_per_point'}, inplace=True)

# if already existing get latest dataframe, append today's dataframe to it and write it to excel
# if today is the first dataframe (e.g. first use of this script) simply write today's dataframe to excel

list_of_files = glob.glob('*.xlsx') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
try:
    df_latest = pd.read_excel(latest_file, index_col=0)
except FileNotFoundError:
    with pd.ExcelWriter(f'{datetime.today().strftime("%Y-%m-%d")}_team_values.xlsx') as writer:
        df_today.to_excel(writer)
else:
    df_concat = pd.concat([df_latest, df_today], axis=0)

    with pd.ExcelWriter(f'{datetime.today().strftime("%Y-%m-%d")}_team_values.xlsx') as writer:
        df_concat.to_excel(writer)
