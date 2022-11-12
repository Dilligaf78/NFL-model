#!/usr/bin/env python
# coding: utf-8

# ### Program to scrape NFL stats
# 

# In[1]:


# install libraries

from bs4 import BeautifulSoup as Soup
import html5lib as htlib
import lxml
import pandas as pd
import numpy as np
import requests as requests
import re
import urllib.parse
from urllib.error import HTTPError
from pathlib import Path


# In[29]:


def make_filepath(path, tablename):
    
    # make a filepath for a cvs file to stare information
    filepath = path + tablename.replace('.', '') + '.csv'
    


# In[30]:


def scrape_table(url, tablename, path):
       
    try:
        
        # get a  list of dataframes (spreadsheets) one dataframe for each table in the page
        tables = pd.read_html(url)
        
    except HTTPError as err:
        
        # if wrong web address print the address for manual review
        if err.code  == 404:
        
            print(url + '404')
            
        # if other HTTP error print the website in question for inspection
        else:
            print(tablename + str(err.code))

            filepath = make_filepath(path, tablename)
        
    # otherwise save the data tables
    else:
        filepath = path + tablename.strip(".") + ".csv"
        tables[0].to_csv(filepath)
        
    return tables   


# In[31]:


# Global variables
path = '~\\NFL_Modeling\\'

# read the team name information
allTeams = pd.read_csv('~\\NFL_Modeling\\all_teams.csv')


# websites to scrape
pfr = 'https://www.pro-football-reference.com/years/2022/'
sonny = 'https://sonnymoorepowerratings.com/nfl-foot.htm'
fbinside = 'https://www.footballoutsiders.com'
nfelo = 'https://www.nfeloapp.com/nfl-power-ratings/'


# First, collect data from https://www.pro-football-reference.com/

# In[43]:


# Get a table of all games for the season
games = pd.read_html('https://www.pro-football-reference.com/years/2022/games.htm#games')
games[0].to_csv('~\\NFL_Modeling\\games.csv')


# In[121]:


# Expand the games to run in both directions
gamesDF = pd.read_csv('~/NFL_Modeling/games.csv')

# rename colums
gamesDF.columns = ['gameid','week', 'day_of_week', 'date', 'time', 'team_full_name', 'home_away', 
                   'def_team', 'played', 'PtsW', 'PtsL', 'YdsW', 'TOW', 'YdsL', 'TOL']

# delete unneccesary columns
dfcolumns = ['played', 'TOW', 'TOL']

for dfcolumn in dfcolumns:
    gamesDF.drop(dfcolumn,inplace = True, axis=1)
    
# drop the rows that are not games
gamesDF.drop(gamesDF.loc[gamesDF['week']=='Week'].index, inplace = True)
    
# move home and away outside of team information
gamesDF = gamesDF.iloc[:, [0, 1, 2, 3, 4, 5, 7, 6, 8, 9, 10, 11] ]

# create a dataframe for the reverse competition - with reidentified column headings
game2DF = gamesDF.rename(columns={'team_full_name':'def_team', 'def_team':'team_full_name', 'PtsW' : 'PtsL', 
                                  'PtsL' : 'PtsW', 'YdsW' : 'YdsL', 'YdsL' : 'YdsW'})

# reorder the dataframe to align with the original
game2DF = game2DF.iloc[:, [0, 1, 2, 3, 4, 6, 5, 7, 9, 8, 11, 10] ]

# identify who is home team and who is away
gamesDF.replace('@','1', inplace = True)
game2DF.replace('@','0', inplace = True)

# remove None values in home/away
gamesDF['home_away'] = gamesDF['home_away'].fillna(0)
game2DF['home_away'] = game2DF['home_away'].fillna(value = 1)

# I think it is ok to combine all games now.
frames = [gamesDF, game2DF]
gamesDF = pd.concat(frames, ignore_index = True)

#  Keep an excel, just in case
gamesDF.to_csv('~\\NFL_Modeling\\allgames.csv')


# In[129]:


# a method to determine how many levels in column headers
def check_header_levels(nfldf):
    
    n = nfldf.columns.nlevels
    
    return n


# In[140]:


# a method to flatten headers in a panda dataframe
def flatten_header(nfldf, n):
    
    i = 0
    
    levelformat = '{0[0]}'
    
    while i < n-1:
        i = i + 1
        levelformat = levelformat + '|{0[' + str(i) +']}'
    
    nfldf.columns = nfldf.columns.map(levelformat.format)
    
    return nfldf


# In[197]:


# remove the practice of adding unnamed levels during flattening

def remove_unnamed(columnheaders):
                  
    n = len(columnheaders)
    i = 0
    newcolumns = []
#for cheader in cheaders:
    while i < n:
        hstr = columnheaders[i]
        if 'Unnamed' in hstr:
            hstr = re.sub('Unnamed.*\|','', hstr)
        i = i + 1
        
        newcolumns.append(hstr)
    
    return newcolumns


# In[190]:


opp = pd.read_html('https://www.pro-football-reference.com/years/2022/opp.htm#team_conversions')
oppdf = opp[0]


# In[198]:


n = check_header_levels(oppdf)
if n > 1:
    oppdf = flatten_header(oppdf, n)

newheaders = remove_unnamed(oppdf.columns)
oppdf.columns = newheaders


# In[199]:


AllpfrDF = pd.read_csv('~\NFL_Modeling\\all_teams.csv')
# iterate through the tables to create dataframes
AllpfrDF = AllpfrDF.merge(oppdf, how = 'left', left_on= "full_team_name", right_on='Tm', validate="1:1")


# In[201]:


# list of sudirectories for tables on nfl reference
tablenames = ['opp.htm#team_stats','opp.htm#team_conversions','opp.htm#advanced_defense', 'opp.htm#passing', 'opp.htm#rushing', 'opp.htm#returns',
              'opp.htm#kicking', 'opp.htm#team_conversions', 'opp.htm#drives', 'index.htm#team_stats', 'index.htm#passing',
              'index.htm#all_rushing', 'index.htm#all_returns', 'index.htm#all_kicking', 'index.htm#all_team_scoring', 
              'index.htm#all_team_conversions', 'index.htm#all_drives']

AllpfrDF = pd.read_csv('~\\NFL_Modeling\\all_teams.csv')
# iterate through the tables to create dataframes
for tablename in tablenames:
    
    # assign the url
    url = pfr + tablename
    
    filename = tablename
    
    # scrape the tables
    tables = scrape_table(url, tablename, path)
    
    # extract the dataframe
    tabledf = tables[0]
    
    # check levels in header
    n = check_header_levels(tabledf)
    if n > 1:
        #flatten if there is more than 1 level
        tabledf = flatten_header(tabledf, n)

        # remove the unnamed from headers with only one level
        newheaders = remove_unnamed(tabledf.columns)
        tabledf.columns = newheaders
  
    AllpfrDF = AllpfrDF.merge(tabledf, how = 'left', left_on= "full_team_name", right_on="Tm")
  
   


# In[208]:


AllpfrDF.head
AllpfrDF.to_csv('~\\NFL_Modeling\\alloff.csv')


# In[225]:


nfelolist = scrape_table(nfelo, 'nfelo', path)
   
# extract the dataframe
nfelodf = tablelist[0]


   


# In[239]:


# check levels in header
n = check_header_levels(nfelodf)
if n > 1:
    #flatten if there is more than 1 level
    nfelodf = flatten_header(nfelodf, n)

    # remove the unnamed from headers with only one level
newheaders = remove_unnamed(nfelodf.columns)
newheaders[0] = 'team'
newheaders[1] = 'nfelo_pwrk'
nfelodf.columns = newheaders
       


for item in nfelodf['team']:
    subitem = re.sub('^\d*', '', item)
    nfelodf['team'] = nfelodf['team'].replace(item, subitem)


# In[31]:


AllnflDF = AllprfDF
allnflDF = AllnflDF.merge(nfeloDF, how='left', left_on='nfelo_name', right_on = 'team')
AllnflDF = AllnflDF.merge(pd.read_csv('~/NFL_Modeling/soonymoore.csv'), how='left', on='full_team_name')
AllnflDF = AllnflDF.merge(pd.read_csv('~/dvoa_off.csv'),how='left', on='full_team_name')
AllDF = pd.merge([gamesDF, pd.read_csv(~/NFL_Modeling/games.htm.csv')], axis = 0)

AllpfrDF.to_csv('~\\NFL_Modeling\\alloff.csv')


# Second, collect data from https://sonnymoorepowerratings.com/nfl-foot.htm

# In[182]:


# scrape the sonny more table
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
}
html = requests.get(sonny,headers=headers)
soup = Soup(html.content, 'html.parser').body.center.pre.font
#souptag = soup.body.center.pre.font

filepath = make_filepath(path, 'sonnymoore')
              
strtable = soup.getText()

table = strtable.split()

# this leaves us with a string of values that still need to be made into a table     
    



# Third, collect data from https://www.footballoutsiders.com/stats/nfl/team-efficiency/2022/regular
# 
# Site is password protected without an account, only 5 lines show up

# In[35]:


tablenames = ['/stats/nfl/team-defense/2020','/stats/nfl/team-offense/2020', '/stats/nfl/team-efficiency/2020', '/stats/nfl/special-teams/2020' ]

# assign url
baseurl = 'https://www.footballoutsiders.com'

# initiate session and login
s = requests.Session()
data =  {'edit-name': emailName,'edit-password':passwordName}
login = s.post(baseurl,data=data)

# iterate through the tables to create dataframes
for tablename in tablenames:
    
    # assign the url
    url = pfr + tablename
    
    filename = tablename
    
    # scrape the tables
    scrape_table(url, tablename, path)


# In[243]:


# put all vegas information in one csv

#recreate file names (  to make this more efficient in the future)
tablenames = allTeams["pfr_abbreviation"]


# create an empty dataframe
vegasDF = pd.DataFrame()

for tablename in tablenames:
    
    # assign the url
    url = 'https://www.pro-football-reference.com/teams/' + tablename + '/2022_lines.htm#vegas_lines'
    
    filename = tablename+'vegas'
    
    # scrape the tables
    tablelists = scrape_table(url, filename, path)
    
    # extract the dataframe
    tabledf = tablelists[0]
    
    # check levels in header
    n = check_header_levels(tabledf)
    if n > 1:
        #flatten if there is more than 1 level
        tabledf = flatten_header(tabledf, n)

        # remove the unnamed from headers with only one level
        newheaders = remove_unnamed(tabledf.columns)
        tabledf.columns = newheaders
  
    vegasDF = pd.concat([vegasDF, tabledf], axis = 0)
    
filepath = path +'allvegas.csv'

vegasDF.to_csv(filepath)

