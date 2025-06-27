
# Extracting Data from Steampowered API to Store into a Database

## Webscraping "Most Played Games" steam page

```python {cmd}
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import requests
import time
import pandas as pd
import numpy as np
import json
import pickleshare

```


The following chunk of code runs a selenium browser to open up steams most played games and mines the website to create a list of links to those game pages. 
Then it extracts the app_id of the game and appends it to our API link to create a list of api's with the app ids we are interested in. 

```python
user_agent = "Microsoft Edge UA string:Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136"
options = webdriver.EdgeOptions()
options.add_argument('user-agent={0}'.format(user_agent))
options.add_argument("--headless=new")

driver = webdriver.Edge()

url = "https://store.steampowered.com/charts/mostplayed/"

links = []
app_ids = []

def get_app_ids(url, rec=False):
    page = driver.get(url)
    response = requests.get(url, user_agent)
    print(response.status_code, url)


    time.sleep(2)

    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN) 

        
    soup = BeautifulSoup(driver.page_source, "html")

    chart = soup.find("div", class_ = "_1A7NagdRz58_o8HPHMa3eE").find("table", class_ = "_3arZn0BMPzyhcYNADe193m")

    for ls in chart.find_all("td"):
        try:  
            link = (ls.find("a", href = True)["href"])
            links.append(link)
            app_id = link.split('/')[4]
            app_ids.append(app_id)

        except Exception as e:   
            None

get_app_ids(url)
    
print(app_ids)


driver.quit()
```
## Creating our Database and Establishing a Connection
Now that the ids for each game are stored we can use an unofficial steam api to pull JSON data about each of the most played games on steam 
But first lets create a database using SQLAlchemy to store our data. 
Note: I used SQLAlchemy because it can easily connect to postgres 

```python
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, URL
from typing import List
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy import update 
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

db_url = URL.create(
    drivername='postgresql+psycopg2', 
    username = 'postgres', 
    password='Notmypassword', 
    host='localhost', 
    port="5432", 
    database='steam_games_details'
)

engine = create_engine(db_url, pool_pre_ping=True)

Base = DeclarativeBase

class Base(DeclarativeBase): 
    pass

class steamGames(Base): 
    __tablename__ = 'games'
    id = mapped_column(Integer, primary_key=True)
    gameid = mapped_column(Integer)
    name = mapped_column(String)
    description = mapped_column(String)
    price = mapped_column(String)
    date = mapped_column(String)

# Note: The following drop table statement may seem odd, but this is to help us update our data with the latest "most played games" information from steam. This is my solution to updating my data, however, this may not be feasible on larger scale projects. 
steamGames.__table__.drop(engine)

    
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
session = Session()
```

## Gathering Games Information

We've now set up the foundation for our database and the table we will be extracting the data into
Finally, let's connect to the third party steam api "steampowered" to gather our data!
We now want to create a function to run all of the collected api links to retreive data from the api and place it into a dataframe. 

```python

def get_game_details(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36","x-requested-with":"XMLHttpRequest"} # add x-requested-with headers here to make sure the output is json format

    response = requests.get(url, headers=headers)
    data = response.json()

    if data[str(app_id)]['success']:
        game_data = data[str(app_id)]['data']

        return game_data


for app_id in app_ids:
    game_data = get_game_details(app_id)
    if 'release_date' in game_data:
        date = game_data['release_date']['date']
    else:
        date = 'coming soon'
    if 'price_overview' in game_data:
            price = game_data['price_overview']['final_formatted']
    else:
        price = 'Free' if game_data['is_free'] else 'price not available'
    steam_games = steamGames(
    gameid = game_data['steam_appid'],
    name = game_data['name'],
    description = game_data['short_description'], 
    price = price, 
    date = date) 
    session.add(steam_games)

try: 
     session.commit()
except: 
     session.rollback()
```

## Preview of table
Our data has now been extracted and added to our games table in our database. 
Lets run a basic select statement to dispaly some of the data that we've stored

```python

from sqlalchemy import select

stmt = select(steamGames)
result = session.execute(stmt)

for steamGames_obj in result.scalars(): 
    print(f"{steamGames_obj.gameid} {steamGames_obj.name} {steamGames_obj.price}")
```

