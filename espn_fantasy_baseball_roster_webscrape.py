# Setup
import pyautogui
import time
import pyperclip
from datetime import date, datetime, timedelta
import pandas as pd
import sys
import logging

# Initialize log
logging.basicConfig(filename='espn_fantasy_webscrape.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger('espn_fantasy_webscrape')

# Set constants and other data
# Coordinate settings
chrome_x_coord = 1028 #second item on taskbar
chrome_y_coord = 1055
notepad_x_coord = 1160 #fifth item on taskbar
notepad_y_coord = 1055
url_x_coord = 178
url_y_coord = 62

# ESPN URL Settings
SWID='{E9FF23A9-48B2-424A-A164-59B896B3E7C6}'
espn_s2='AEC0A9uRI4UcP%2BQaf2mzqcQ4%2FvLD30E%2BYs6OvMvDFJSKssDG%2FSbwzRadgP9%2FI5DC4jigFV8YrsJavlObSfV%2BOlQsgM2lx%2FPBSkb25tqC9ANwSKrIopTKiVMJSgeTrAv8WZhfyGD0QZOIZvf1JlJ1hwZGXpzfDtfi9jPRR7RTjmN%2Ba0FLJIjMYU3cvd%2FKcuJiIJFP11qtwMXCqBLFk60dtcc5bMUMZlyoIM21NMz5HTil7QslkcMhdnmahL2ysjWL6i4%3D'
url_base='https://fantasy.espn.com/baseball/team?'

# League settings
league_id=150785
league_calendar=[#(2019, date.fromisoformat("2019-03-20"), 166), 
				 #(2020, date.fromisoformat("2020-03-26"), 179),
				 #(2021, date.fromisoformat("2021-04-01"), 158),
				 #(2022, date.fromisoformat("2022-04-07"), 158)
				 (2023, date.fromisoformat("2023-03-30"), 144)
				]
league_teams=[1,2,3,4,5,6,7,8,9,10,11,12] #limited to one team for testing purposes

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
	
def espn_fantasy_textparse():
	# Open the file
	f=open("paste_test.txt", "r")
	f_list = f.readlines()

	# Scan for matching position names, capture matches and store result
	player_name_list = []
	positions = ["C\n", "1B\n", "2B\n", "3B\n", "SS\n", "OF\n", "UTIL\n", "Bench\n", "IL\n", "SP\n", "RP\n"]
	for pos in positions:
		for line in range(len(f_list)):
			test_line = f_list[line]
			# Filter out short/all-caps strings that are probably not player names
			if test_line == pos and len(f_list[line+2]) > 6 and f_list[line+2].isupper()==False:
				# Remove newline characters from end of string
				player_name = f_list[line+2][:-1]
				player_tuple = (pos[:-1], player_name)
				player_name_list.append(player_tuple)
	return(player_name_list)
	
def check_espn_csv():
	# Read the csv file
	chk_file = pd.read_csv(str(league_calendar[year][0])+'_'+str(team_id)+'_'+'roster.csv')
	# Flag any scoring periods with fewer than 20 players rostered
	failed_chk = chk_file.groupby(['scoring_period_id']).size().to_frame(name='roster_cnt').reset_index()
	failed_chk = failed_chk.loc[failed_chk['roster_cnt'] < 20]
	for j in range(len(failed_chk)):
		logger.info(str(failed_chk['scoring_period_id'][j])+' failed check')


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
f=open("paste_test.txt", "r")
f_list = f.readlines()
test_statement = f_list[0][:2]
if test_statement == 'NO':
	pyautogui.alert('Test passed; windows are positioned correctly.')
else:
	pyautogui.alert('Test failed; please reposition windows.')
	sys.exit()


### EXECUTE WEBSCRAPE

# Loop over every team-season to collect roster data for each day
for year in range(len(league_calendar)):
	for team_id in league_teams:
		# Initialize dataframe and league start date
		roster = pd.DataFrame(columns=['year', 'team_id', 'scoring_period_id', 'date', 'player_name', 'player_pos'])
		current_dt = league_calendar[year][1]
		scoring_period_id=1 #Always start with the first scoring period
		for day in range(league_calendar[year][2]):
			# Create URL
			final_url=url_base+'seasonId='+str(league_calendar[year][0])+'&leagueId='+str(league_id)+'&teamId='+str(team_id)+'&scoringPeriodId='+str(scoring_period_id)+'&view=stats&SWID='+SWID+'&espn_s2='+espn_s2
			logger.info(final_url)
			pyperclip.copy(final_url)
			# Paste to Chrome, go, and copy
			espn_fantasy_webscrape()
			# Parse the text
			player_name_list = espn_fantasy_textparse()
			logger.info(str(scoring_period_id) + ' ' + str(current_dt) + ' ' + str(len(player_name_list)))
			# Write to dataframe
			for i in range(len(player_name_list)):
				new_row = [league_calendar[year][0], team_id, scoring_period_id, current_dt, player_name_list[i][1], player_name_list[i][0]]
				roster.loc[len(roster)] = new_row
			# Increment scording_period_id and date
			scoring_period_id+=1
			current_dt=current_dt+timedelta(days=+1)
		# Export roster
		roster.to_csv(str(league_calendar[year][0])+'_'+str(team_id)+'_'+'roster.csv', index=False)
		# Check CSV and log any potential errors
		check_espn_csv()
