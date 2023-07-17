# Setup
import pyautogui
import time
import pyperclip
from datetime import date, datetime, timedelta
import pandas as pd
import sys
import logging
import math

# Initialize log
logging.basicConfig(filename='espn_fantasy_score_webscrape.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger('espn_fantasy_score_webscrape')

# Set constants and other data
# Coordinate settings
chrome_x_coord = 1052 #second item on taskbar
chrome_y_coord = 1055
notepad_x_coord = 1182 #fifth item on taskbar
notepad_y_coord = 1055
url_x_coord = 155
url_y_coord = 53

# ESPN URL Settings
SWID='{E9FF23A9-48B2-424A-A164-59B896B3E7C6}'
espn_s2='AEC0A9uRI4UcP%2BQaf2mzqcQ4%2FvLD30E%2BYs6OvMvDFJSKssDG%2FSbwzRadgP9%2FI5DC4jigFV8YrsJavlObSfV%2BOlQsgM2lx%2FPBSkb25tqC9ANwSKrIopTKiVMJSgeTrAv8WZhfyGD0QZOIZvf1JlJ1hwZGXpzfDtfi9jPRR7RTjmN%2Ba0FLJIjMYU3cvd%2FKcuJiIJFP11qtwMXCqBLFk60dtcc5bMUMZlyoIM21NMz5HTil7QslkcMhdnmahL2ysjWL6i4%3D'
url_base='https://fantasy.espn.com/baseball/league/scoreboard?'

# League settings
league_id=150785
league_calendar=[(2018, 21),
				 (2019, 21), 
				 (2020, 8),
				 (2021, 21),
				 (2022, 21)
				]
league_teams=[1,2,3,4,5,6,7,8,9,10,11,12]
team_names = pd.read_csv('team_name_lookup.csv', sep=';', encoding='cp1252')

# Define functions
def espn_fantasy_webscrape():
	# Navigate to ESPN window and paste URL into bar
	pyautogui.click(chrome_x_coord, chrome_y_coord)
	pyautogui.moveTo(url_x_coord, url_y_coord, duration=0.5, tween=pyautogui.easeInOutQuad)
	pyautogui.click()
	pyautogui.hotkey('ctrl', 'v')
	pyautogui.press('enter')
	# Wait 3 seconds for the webpage to load, copy all
	time.sleep(5)
	pyautogui.hotkey('ctrl', 'a')
	pyautogui.hotkey('ctrl', 'c')
	# Click back to Notepad; clear, paste and save
	pyautogui.click(notepad_x_coord, notepad_y_coord)
	pyautogui.hotkey('ctrl', 'a')
	pyautogui.press('backspace')
	pyautogui.hotkey('ctrl', 'v')
	pyautogui.hotkey('ctrl', 's')
	
def espn_fantasy_score_textparse(league_year, matchup_period):
	# Open the file
	f=open("scoreboard_paste.txt", "r", encoding="cp1252")
	f_list = f.readlines()
	
	# Create empty dataframe to store results
	scores = pd.DataFrame(columns=['year','matchup_period','matchup_date','team','score','matchup_id'])
	
	# Create a list of team names for the provided league year
	team_names_current_year = team_names.loc[team_names.year==league_year]['team_name'].values.tolist()
	for j in range(len(team_names_current_year)):
		team_names_current_year[j] = team_names_current_year[j].replace("’","'")
	
	# Scan file for matchup date
	for j in range(len(f_list)):
		if f_list[j][0:-1] == 'Matchups':
			matchup_date = f_list[j+1][0:-1]
	
	# Save lines that correspond to matchup period and score
	matchup_id_counter = 1
	for j in range(len(f_list)):
		if f_list[j][0:-1] in team_names_current_year:
			team = f_list[j][0:-1]
			score = f_list[j+2][0:-1]
			matchup_id = math.ceil(matchup_id_counter/2)
			matchup_id_counter = matchup_id_counter + 1
			new_row = [league_year, matchup_period, matchup_date, team, score, matchup_id]
			scores.loc[len(scores)] = new_row
		
	# # List of lookup positions for each score and team
	# score_positions = [(99,103),(108,112),(117,121),(126,130),(135,139),(144,148)]
	# team_positions = [(97,101),(106,110),(115,119),(124,128),(133,137),(142,146)]
	
	# # Read matchup date and number
	# matchup_date = f_list[93]
	
	# # Read teams and scores for all six matchups each week
	# for i in range(6):
		# new_row = [league_year, matchup_period, matchup_date, f_list[team_positions[i][0]-1], f_list[team_positions[i][1]-1], f_list[score_positions[i][0]-1], f_list[score_positions[i][1]-1]]
		# scores.loc[len(scores)] = new_row

	return(scores)

### TEST WINDOW POSITIONING BEFORE WEBSCRAPE

# Place "isitchristmas.com" into the notepad file
# Navigate to Notepad window
pyautogui.click(notepad_x_coord, notepad_y_coord)
pyautogui.hotkey('ctrl', 'a')
pyautogui.hotkey('ctrl', 'c')

# Navigate to URL bar
pyautogui.click(chrome_x_coord, chrome_y_coord)
pyautogui.click(url_x_coord, url_y_coord)
pyautogui.hotkey('ctrl', 'v')
pyautogui.press('enter')
# Wait 5 seconds for the webpage to load
time.sleep(5)
pyautogui.hotkey('ctrl', 'a')
pyautogui.hotkey('ctrl', 'c')

# Navigate to Notepad, paste and save
pyautogui.click(notepad_x_coord, notepad_y_coord)
pyautogui.hotkey('ctrl', 'v')
pyautogui.hotkey('ctrl', 's')

# Read file and test output
f=open("scoreboard_paste.txt", "r")
f_list = f.readlines()
test_statement = f_list[0][:2]
if test_statement == 'NO':
	pyautogui.alert('Test passed; windows are positioned correctly.')
else:
	pyautogui.alert('Test failed; please reposition windows.')
	sys.exit()


### EXECUTE WEBSCRAPE

# Loop over every season and matchup period to collect score data for each week
for year in range(len(league_calendar)):
	# Initialize output dataframe
	scores_output = pd.DataFrame(columns=['year','matchup_period','matchup_date','team','score','matchup_id'])
	for matchup in range(league_calendar[year][1]):
		# Create URL
		final_url=url_base+'seasonId='+str(league_calendar[year][0])+'&leagueId='+str(league_id)+'&matchupPeriodId='+str(matchup+1)+'&SWID='+SWID+'&espn_s2='+espn_s2
		logger.info(final_url)
		pyperclip.copy(final_url)
		# Paste to Chrome, go, and copy
		espn_fantasy_webscrape()
		# Parse the text
		add_to_dataframe = espn_fantasy_score_textparse(league_calendar[year][0], matchup+1)
		# Add to dataframe
		scores_output = pd.concat([scores_output,add_to_dataframe])
	# Write dataframe
	scores_output.to_csv(str(league_calendar[year][0])+'_'+'scores.csv', index=False)
