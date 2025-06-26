#Extracting Data from Steampowered API to Store into a Database Part 2: Expanding our database

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from typing import List
from typing import Optional
from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
import psycopg2

# Connecting to our postgres database using SQLAlchemy

db_url = URL.create(
    drivername='postgresql+psycopg2', 
    username = 'postgres', 
    password='Notmypassword', 
    host='localhost', 
    port="5432", 
    database='steam_games_details'
)

engine = create_engine(db_url)

Base = DeclarativeBase

class Base(DeclarativeBase): 
    pass


class steamReviews(Base): 
    __tablename__ = 'reviews'
    id = mapped_column(Integer, primary_key=True)
    appid = mapped_column(Integer)
    forever_playtime = mapped_column(Integer)
    past_two_week_playtime = mapped_column(Integer)
    review = mapped_column(String)

# The following drop table statement may seem odd, but this is to help us update our data with the latest "most played games" information from steam 
# Note: This is my solution to updating my data, however, this may not be feasible on larger scale projects. 

steamReviews.__table__.drop(engine)
    
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
session = Session()

try:
    connection = engine.connect()
    print("Connection successful!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")



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
import sqlite3
import pickleshare

# appids have already mined and parsed in our last program steamGames.py, so let's import them.
from steamGames import app_ids
    
print(app_ids)

#Now that all of the set up is complete, lets use our API link to retreive some reveiws and other interesting player information.

def get_reviews(app_id):
    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1"
    response = requests.get(url)
    data = response.json()
    
    Users = data['reviews']

    return Users

for app_id in app_ids: 
    for Users in get_reviews(app_id): 
        steam_reviews = steamReviews(
        appid = app_id,
        forever_playtime = Users['author']['playtime_forever'],
        past_two_week_playtime = Users['author']['playtime_last_two_weeks'],
        review = Users['review'])
        session.add(steam_reviews)


try: 
    session.commit()
except: 
    session.rollback()

    
query = session.query(steamReviews)

print(query)

#The data is now stored in the "reviews" table in our database.
#lets take a look at some reviews!

from sqlalchemy import select

stmt = select(steamReviews)
result = session.execute(stmt)

for steamReviews_obj in result.scalars(): 
    print(f"{steamReviews_obj.appid} {steamReviews_obj.forever_playtime} {steamReviews_obj.review}")