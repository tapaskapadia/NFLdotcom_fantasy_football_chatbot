# NFl.com Fantasy Football GroupMe Chatbot

NFLdotcom_fantasy_football_chatbot is a GroupMe chatbot that provides power rankings, score updates, matchup alerts, ect. for nfl.com fantasy football leagues. 


## Installation

#### Prerequisites
Requires python3 

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install NfldotcomFantasyFootballBot.

Create a new bot for the GroupMe group [here]( https://dev.groupme.com/bots/) and make note of the bot id created.

```bash
cp .env.example .env
```

Make sure to replace REPLACE_WITH_GROUPME_BOT_ID and REPLACE_WITH_PUBLIC_LEAGUE_URL with appropriate values.

```bash
pip3 install -r requirements.txt
```

## Usage

```python
cp .env.example .env
# replace BOT_ID with your GroupMe Bot ID and league url.
#link to create new GroupMe Bot: https://dev.groupme.com/bots
python3 groupMeBot.py
```