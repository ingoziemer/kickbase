from kickbase_api.kickbase import Kickbase
import pandas as pd
from datetime import datetime, timedelta
import os

pd.options.display.float_format = '{:,.2f}'.format
# gets user credentials from environment variables and logs in
USERNAME = os.getenv("kickbase_user")
PASSWORD = os.getenv("kickbase_pw")

kickbase = Kickbase()
user, league = kickbase.login(username=USERNAME, password=PASSWORD)

# choose league
DFS = league[0]

# get the players on your team and write their names and market value in a dataframe
user_players = kickbase.league_user_players(DFS, user=user)

player_names = []
player_market_values = []
day = []
for row in range(len(user_players)):
    player_names.append(user_players[row].last_name)
    player_market_values.append(user_players[row].market_value)
    day.append(datetime.today().strftime("%Y-%m-%d"))

data = [day, player_names, player_market_values]
df_today = pd.DataFrame(data).T

df_today.rename(columns={0: 'date', 1: 'name', 2: 'market_value'}, inplace=True)

# if already existing get yesterday's dataframe, append today's dataframe to it and write it to excel
# if today is the first dataframe (e.g. first use of this script) simply write today's dataframe to excel
yesterday = datetime.today() - timedelta(days=1)
yesterday.strftime("%Y-%m-%d")
try:
    df_yesterday = pd.read_excel(f'{yesterday.strftime("%Y-%m-%d")}_team_values.xlsx', index_col=0)
except FileNotFoundError:
    with pd.ExcelWriter(f'{datetime.today().strftime("%Y-%m-%d")}_team_values.xlsx') as writer:
        df_today.to_excel(writer)
else:
    df_concat = pd.concat([df_yesterday, df_today], axis=0)

    with pd.ExcelWriter(f'{datetime.today().strftime("%Y-%m-%d")}_team_values.xlsx') as writer:
        df_concat.to_excel(writer)
