#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go #data visualization for Python
pd.set_option('display.max_columns', None) #display all the columns in a wide dataframe

data=pd.read_excel('nba_stats.xlsx')


# In[2]:


data.sample(15) #random sample of 15 players and their stats
                #in order to be in this data set you must have played at least one game


# In[3]:


data.shape #size of the dataframe


# # Data Cleaning & Analysis Preparation

# In[4]:


data.drop(columns=['RANK', 'EFF'], inplace=True)


# In[5]:


data['season_start_year']= data['Year'].str[:4].astype(int) #make sure it is in an integer format


# In[6]:


data.TEAM.unique()


# In[7]:


data.TEAM.nunique() #checks the number of teams


# In[8]:


data['Season_type'].replace('Regular%20Season', 'RS', inplace=True) #replace 'Regular%20Season' with 'RS'


# In[9]:


#delcare one dataframe for the regular season and one for the playoffs
rs_df = data[data['Season_type']=='RS']
playoffs_df = data[data['Season_type']=='Playoffs'] 


# In[10]:


data.columns


# In[11]:


#reduce the unnecessary columns
total_cols = ['MIN', 'FGM', 'FGA','FG3M', 'FG3A','FTM', 'FTA',
             'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF','PTS'] 


# # Which player stats are correlated with each other?

# In[12]:


#group by each player in any given season and their stats
data_per_min = data.groupby(['PLAYER','PLAYER_ID','Year'])[total_cols].sum().reset_index()
for col in data_per_min.columns[4:]:
        data_per_min[col] = data_per_min[col]/data_per_min['MIN']

data_per_min['FG%'] = data_per_min['FGM']/data_per_min['FGA']
data_per_min['3PT%'] = data_per_min['FG3M']/data_per_min['FG3A']
data_per_min['FT%'] = data_per_min['FTM']/data_per_min['FTA']
data_per_min['FG3A%'] = data_per_min['FG3A']/data_per_min['FGA']
data_per_min['PTS/FGA'] = data_per_min['PTS']/data_per_min['FGA']
data_per_min['FG3M/FGM'] = data_per_min['FG3M']/data_per_min['FGM']
data_per_min['FTA/FGA'] = data_per_min['FTA']/data_per_min['FGA']
data_per_min['TRU%'] = 0.5*data_per_min['PTS']/(data_per_min['FGA']+0.475*data_per_min['FTA'])
data_per_min['AST_TOV'] = data_per_min['AST']/data_per_min['TOV']


data_per_min = data_per_min[data_per_min['MIN']>=50]
data_per_min.drop(columns='PLAYER_ID', inplace=True)

fig = px.imshow(data_per_min.corr(numeric_only=True))
fig.show()


# In[13]:


(data_per_min['MIN'] >=50).mean() #player needs to play at least 50 mins


# # How are minutes played distributed?

# In[14]:


#fig = px.histogram(x=rs_df['MIN'], histnorm='percent') #shows how much mins are played
fig = px.histogram(x=playoffs_df['MIN'], histnorm='percent') #this shows the playoffs mins
fig.show()


# In[15]:


def hist_data(df=rs_df, min_MIN=0, min_GP=0):
     return df.loc[(df['MIN']>=min_MIN) & (df['GP']>=min_GP), 'PTS']/\
    df.loc[(df['MIN']>=min_MIN) & (df['GP']>=min_GP), 'GP']


# In[16]:


#shows the difference between points and averages on regular seasons and playoffs
fig=go.Figure()
fig.add_trace(go.Histogram(x=hist_data(rs_df,50,5), histnorm='percent', name='RS', 
                           xbins={'start':0, 'end':38, 'size':1}))
fig.add_trace(go.Histogram(x=hist_data(playoffs_df,5,1), histnorm='percent', name='Playoffs',
                           xbins={'start':0, 'end':38, 'size':1}))

fig.update_layout(barmode='overlay')
fig.update_traces(opacity=0.5)
fig.show()


# In[17]:


((hist_data(rs_df,50,5)>=12)&(hist_data(rs_df,50,5)<=34)).mean()


# In[18]:


((hist_data(playoffs_df,5,1)>=12)&(hist_data(playoffs_df,5,1)<=34)).mean()


# # How has the game changed in the past 10 years?

# In[19]:


change_df = data.groupby('season_start_year')[total_cols].sum().reset_index()
change_df['POSS_est'] = change_df['FGA']-change_df['OREB']+change_df['TOV']+0.44*change_df['FTA']
change_df[list(change_df.columns[0:2])+['POSS_est']+list(change_df.columns[2:-1])]

change_df['FG%'] = change_df['FGM']/change_df['FGA']
change_df['3PT%'] = change_df['FG3M']/change_df['FG3A']
change_df['FT%'] = change_df['FTM']/change_df['FTA']
change_df['AST%'] = change_df['AST']/change_df['FGM']
change_df['FG3A%'] = change_df['FG3A']/change_df['FGA']
change_df['PTS/FGA'] = change_df['PTS']/change_df['FGA']
change_df['FG3M/FGM'] = change_df['FG3M']/change_df['FGM']
change_df['FTA/FGA'] = change_df['FTA']/change_df['FGA']
change_df['TRU%'] = 0.5*change_df['PTS']/(change_df['FGA']+0.475*change_df['FTA'])
change_df['AST_TOV'] = change_df['AST']/change_df['TOV']

change_df


# In[20]:


#all of the average stats for the entire season per 48 mins on a given team
#note you can see the FG3M, you can see the increase of three point shots
#you can also see the POSS_est - meaning the possessions her game as increase. The pace the teams are play on. 
change_per48_df = change_df.copy()
for col in change_per48_df.columns[2:18]:
        change_per48_df[col] = (change_per48_df[col]/change_per48_df['MIN'])*48*5
change_per48_df


# In[21]:


change_per48_df = change_df.copy()
for col in change_per48_df.columns[2:18]:
        change_per48_df[col] = (change_per48_df[col]/change_per48_df['MIN'])*48*5

change_per48_df.drop(columns='MIN', inplace=True)

fig = go.Figure()
for col in change_per48_df.columns[1:]:
        fig.add_trace(go.Scatter(x=change_per48_df['season_start_year'],
                                y=change_per48_df[col], name=col))
fig.show()    


# In[22]:


#all of the average stats for the entire season per 100 mins on a given team
#note you can see the FG3M, you can see the increase of three point shots
#you can also see the POSS_est - meaning the possessions her game as increase. The pace the teams are play on. 
change_per100_df = change_df.copy()
for col in change_per100_df.columns[2:18]:
    change_per100_df[col] = (change_per100_df[col]/change_per100_df['POSS_est'])*100

change_per100_df.drop(columns=['MIN','POSS_est'], inplace=True)

change_per100_df


# In[23]:


change_per100_df = change_df.copy()

for col in change_per100_df.columns[2:18]:
        change_per100_df[col] = (change_per100_df[col]/change_per100_df['POSS_est'])*100 

change_per100_df.drop(columns=['MIN','POSS_est'], inplace=True)
change_per100_df

fig = go.Figure()
for col in change_per100_df.columns[1:]:
        fig.add_trace(go.Scatter(x=change_per100_df['season_start_year'],
                                y=change_per100_df[col], name=col))
fig.show()


# # Regular Season v. Playoffs

# In[24]:


#comparing Regular Season v. Playoffs data per 100 possessions
rs_change_df = rs_df.groupby('season_start_year')[total_cols].sum().reset_index()
playoffs_change_df = playoffs_df.groupby('season_start_year')[total_cols].sum().reset_index()

for i in[rs_change_df,playoffs_change_df]:
    i['POSS_est'] = i['FGA']-i['OREB']+i['TOV']+0.44*i['FTA']
    i['POSS_per_48'] = (i['POSS_est']/i['MIN'])*48*5
        
    i['FG%'] = i['FGM']/i['FGA']
    i['3PT%'] = i['FG3M']/i['FG3A']
    i['FT%'] = i['FTM']/i['FTA']
    i['AST%'] = i['AST']/i['FGM']
    i['FG3A%'] = i['FG3A']/i['FGA']
    i['PTS/FGA'] = i['PTS']/i['FGA']
    i['FG3M/FGM'] = i['FG3M']/i['FGM']
    i['FTA/FGA'] = i['FTA']/i['FGA']
    i['TRU%'] = 0.5*i['PTS']/(i['FGA']+0.475*i['FTA'])
    i['AST_TOV'] = i['AST']/i['TOV']
    for col in total_cols:
        i[col] = 100*i[col]/i['POSS_est']
    i.drop(columns=['MIN','POSS_est'], inplace=True)
rs_change_df   


# In[25]:


#percentage change between the regular season and playoffs
comp_change_df = round (100*(playoffs_change_df-rs_change_df)/rs_change_df,3)
comp_change_df['season_start_year'] = list (range(2014,2023))

comp_change_df


# In[26]:


fig = go.Figure()
for col in comp_change_df.columns[1:]:
        fig.add_trace(go.Scatter(x=comp_change_df['season_start_year'],
                                y=comp_change_df[col], name=col))
fig.show()

