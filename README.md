<image> ![image](https://github.com/user-attachments/assets/cc357f42-9b1a-4d61-a210-acbf363f4cd1)

<h1>Welcome to my Most Played Steam Games data collection project!</h1> 

In this project I will use webscraping techniques, packages such as Selenium, requests, and BeautifulSoup, JSON and a few others to extract data, from steam and the unofficial steam api, and build a database in postgres using SQLAlchemy and python.
The ultimate goal is to add tables and potential visualizations to my website in an effort to display my skills in data management, data visualization, and analytics. 

This project is spread out into multiple pieces and is currently still in progress. Although, I have managed to make significant progress. 

<h2> What has been completed</h2>

+ **steamGames.py**: Here I take the links from the Most Played Steam Games page on steam.com to extract gameids and use those ids to refrence json files in the unofficial steam api. 
+ **steamReviews.py**: Similar to steamGames we use game ids to pull over 30,000 data points for the games we pulled in steamGames.py

<h2>In progress</h2>

+ **Topic Modelying Analysis of reviews** 
+ **Topic Modelying of Game Descriptions** 


