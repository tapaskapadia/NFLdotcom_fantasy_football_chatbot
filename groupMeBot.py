from bs4 import BeautifulSoup
import urllib3
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import re
import random
import json
import os
from dotenv import load_dotenv

http = urllib3.PoolManager()

class GroupMeBot(object):
    #Creates GroupMe Bot to send messages
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def __repr__(self):
        return "GroupMeBot(%s)" % self.bot_id

    def send_message(self, text):
        #Sends a message to the chatroom
        template = {
                    "bot_id": self.bot_id,
                    "text": text,
                    "attachments": []
                    }

        headers = {'content-type': 'application/json'}

        if self.bot_id not in (1, "1", ''):
            r = http.request("POST","https://api.groupme.com/v3/bots/post", body=json.dumps(template), headers=headers)
            if r.status != 202:
                raise Exception('Invalid BOT_ID')
            return r

def runner(action):
    try:
        bot_id = os.environ["BOT_ID"]
    except KeyError:
        print("DID NOT FIND BOT_ID ")
        raise Exception("BOT_ID Required to be set as an environment variable")    
    try:
        league_url = os.environ["LEAGUE_URL"]
    except KeyError:
        raise Exception("LEAGUE_URL required to be set as an environment variable") 
    
    bot = GroupMeBot(bot_id)
    try: 
        if action == "getMatchups":
            out = getMatchups(league_url)
        elif action == "scoreCheck":
            out = scoreCheck(league_url)
        elif action == "loserOfTheWeek":
            out = loserOfTheWeek(league_url)
        elif action == "powerRankings":
            out = powerRankings(league_url)
        if out:
            bot.send_message(out)
    except:
        "Error - Something went wrong"

def getManagers(league_url):   
    #url = "https://fantasy.nfl.com/league/986877/owners"
    url = league_url+ "/owners"
    response = http.request('GET', url, headers={'Content-Type':'text/html'})
    soup = BeautifulSoup(response.data, "html.parser")
    teamdata = []
    table = soup.find('table', attrs={'class':'tableType-team'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        teamdata.append([ele for ele in cols if ele])
    teamManagersMap = {}
    for team in teamdata:
        if (len(team) > 2 ):
            teamManagersMap[team[0]] = team[1].strip()
    return teamManagersMap
def getMatchups(league_url):
    #url = "https://fantasy.nfl.com/league/986877/team/6/gamecenter"
    url = league_url+"/team/2/gamecenter"
    response = http.request('GET', url, headers={'Content-Type':'text/html'})
    soup = BeautifulSoup(response.data, "html.parser")
    week = soup.find('li', attrs={'class':'wl'}).getText()
    titles = soup.find('div', attrs={'class':'teamNav'}).find_all("a")
    managers = getManagers(league_url)
    matchups = []
    for title in titles:
        matchupsRaw = title["title"]
        teams = [t.strip() for t in matchupsRaw.split('vs.')]
        if managers and len(teams) > 1:
            matchupText = teams[0] + " (" + managers[teams[0]] + ") vs. " + teams[1] + " (" + managers[teams[1]] + ")"
            matchups.append(matchupText)
    if not matchups:
        return('')
    outputMatchups = ['['+ week +' Matchups]'] + matchups
    return '\n\n'.join(outputMatchups)
#print(getMatchups())
#getManagers()
def getWeek(league_url):
    #url = "https://fantasy.nfl.com/league/986877/team/6/gamecenter"
    url = league_url + "/team/6/gamecenter"
    response = http.request('GET', url, headers={'Content-Type':'text/html'})
    soup = BeautifulSoup(response.data, "html.parser")
    week = soup.find('li', attrs={'class':'wl'}).getText()
    return week
def scoreCheck(league_url):
    #url = "https://fantasy.nfl.com/league/986877/team/6/gamecenter"
    url = league_url + "/team/2/gamecenter"
    response = http.request('GET', url, headers={'Content-Type':'text/html'})
    soup = BeautifulSoup(response.data, "html.parser")
    scoresElements = soup.find('div', attrs={'class':'teamNav'}).find_all("a")
    scoreText = []
    for score in scoresElements:
        scoreText.append(score.getText())
    outScores = ['[Score Check]'] + scoreText
    return '\n\n'.join(outScores)

def random_loser_phrase():
    phrases = ['Congratulations to REPLACE_TEAM, you are trash! REPLACE_POINTS !?',
               'Please take a moment of silence for the tragedy that was REPLACE_TEAM\'s team this week with REPLACE_POINTS points.',
               'Hey look I found REPLACE_TEAM\'s team: 🗑️. REPLACE_POINTS points is sad.',
               'Congratulations REPLACE_TEAM you played yourself. Only REPLACE_POINTS points?',
               '😬 REPLACE_TEAM - REPLACE_POINTS 😬',
               'REPLACE_TEAM that performance was 💩 - REPLACE_POINTS!?',
               'REPLACE_TEAM - REPLACE_POINTS 👎',
               'It was not REPLACE_TEAM\'s week... only putting up REPLACE_POINTS points']
    return random.choice(phrases)

def loserOfTheWeek(league_url):
    week = int(getWeek(league_url).split(' ')[1]) - 1
    if (week > 0):
        #url = "https://fantasy.nfl.com/league/986877/team/6/gamecenter?week={}".format(week)
        url = "{}/team/2/gamecenter?week={}".format(league_url,week)
        response = http.request('GET', url, headers={'Content-Type':'text/html'})
        soup = BeautifulSoup(response.data, "html.parser")
        week = int(soup.find('li', attrs={'class':'wl'}).getText().split(" ")[1])
        managers = getManagers(league_url)
        scoresElements = soup.find('div', attrs={'class':'teamNav'}).find_all("a")
        loserPointArray = []
        for score in scoresElements:
            text = score.getText()
            teams = re.findall('[^0-9\.]+ ', text)
            scores = re.findall('[0-9\.]+ | [0-9\.]+', text)
            ret = [(teams[0].strip(),scores[0].strip()),(teams[1].strip(),scores[1].strip())]
            loserPointArray.extend(ret)
        loser = min(loserPointArray, key = lambda t: t[1])
        phrase = random_loser_phrase()
        replaced_phrase = phrase.replace("REPLACE_TEAM",managers[loser[0]]).replace("REPLACE_POINTS",loser[1])
        outText = '[Loser of Week #{} Report] \n\n {}'.format(week,replaced_phrase)
        return outText
    else: 
        return "Error finding this weeks loser"

def getTeamPointsAllWeek(league_url,week_num=None):
    currweek = week_num or int(getWeek(league_url).split(' ')[1])
    teamPointMap = {}
    for week in range(1,currweek):
        url = "{}/team/6/gamecenter?week={}".format(league_url,week)
        response = http.request('GET', url, headers={'Content-Type':'text/html'})
        soup = BeautifulSoup(response.data, "html.parser")
        scoresElements = soup.find('div', attrs={'class':'teamNav'}).find_all("a")
        for score in scoresElements:
            text = score.getText()
            teams = re.findall('[^0-9\.]+ ', text)
            scores = re.findall('[0-9\.]+ | [0-9\.]+', text)
            teamPointMap.setdefault(teams[0].strip(),[]).append(float(scores[0]))
            teamPointMap.setdefault(teams[1].strip(),[]).append(float(scores[1]))
    return teamPointMap
#Uses The Oberon Mt. Power Rating Formula 
#((avg score x 6) + [(high score + low score) x 2] +[ (winning % x 200) x 2])/10
#http://www.okiraqi.org/opr.html#:~:text=Power%20Rating%20Formula%20combines%20Average,just%20by%20Win%2DLoss%20Record.
def powerRankings(league_url,week_num=None):
    allWeeksTeam = getTeamPointsAllWeek(league_url,week_num=week_num)
    powerRankArry = []
    #url = "https://fantasy.nfl.com/league/986877/"
    url = league_url
    response = http.request('GET', url, headers={'Content-Type':'text/html'})
    soup = BeautifulSoup(response.data, "html.parser")
    rawdata = []
    leagueStats = soup.find('table', attrs={'class':'tableType-team'}).find('tbody').find_all('tr')
    for row in leagueStats:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        rawdata.append([ele for ele in cols if ele]) # 
    for teamData in rawdata:
        if len(teamData) == 9:
            teamName = teamData[1]
            avg_score  = sum(allWeeksTeam[teamData[1]])/len(allWeeksTeam[teamData[1]])
            high_low = (max(allWeeksTeam[teamData[1]])+min(allWeeksTeam[teamData[1]]))*2
            winning = float(teamData[3]) * 200
            powerRankScore = (avg_score + high_low + winning)/10
            powerRankArry.append((teamData[1],powerRankScore))   
    powerRankArry.sort(key = lambda x: x[1], reverse=True) 
    outputPowerRank = '[Weekly Power Rankings Report] \n\n' + "\n".join(map(str, powerRankArry))
    return outputPowerRank

def healthCheck():
    print("UP")

if __name__ == '__main__':
    load_dotenv()
    sched = BlockingScheduler()
    sched.add_job(healthCheck,'interval',seconds=600)
    sched.add_job(runner, 'cron',['scoreCheck'], day_of_week='fri,mon', hour=9, timezone='America/New_York', replace_existing=True)
    sched.add_job(runner, 'cron',['scoreCheck'], day_of_week='sun', hour='16,20', timezone='America/New_York', replace_existing=True)
    sched.add_job(runner, 'cron', ['loserOfTheWeek'], day_of_week='tue', hour=9, timezone='America/New_York', replace_existing=True)
    sched.add_job(runner, 'cron', ['getMatchups'], day_of_week='thu', hour=18,minute=30, timezone='America/New_York', replace_existing=True)
    sched.add_job(runner, 'cron', ['powerRankings'], day_of_week='tue', hour=18,minute=30, timezone='America/New_York', replace_existing=True)
    sched.start()