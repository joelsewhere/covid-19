import requests
import json
import pandas as pd
from colour import Color
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Query API
states = requests.get('https://covidtracking.com/api/states/daily').json()
states = pd.DataFrame(states)

us = requests.get('https://covidtracking.com/api/us/daily').json()
us = pd.DataFrame(us)

# Format Data
states.date = pd.to_datetime(states.date, format = '%Y%m%d')
us.date = pd.to_datetime(us.date, format = '%Y%m%d')

states.set_index('date', inplace = True)
us.set_index('date', inplace =  True)
today = states.loc[states.index.max()]

##################################### GRAPHING ###########################################

# NATIONAL POSITIVE
plt.style.use('dark_background')
fig = plt.figure(figsize=(15,5))
us.positive.plot(linewidth=3, marker = 'o', markersize=10)
plt.title('Positive Test Results COVID-19')
plt.grid()

fig.savefig('images/positive_tests.png')

# NATIONAL DEATHS
fig = plt.figure(figsize=(15,5))
us.death.dropna().plot(linewidth=3, marker = 'o', markersize=10)
plt.title('US Deaths')
plt.grid()

fig.savefig('images/deaths.png')

# POSITIVE GROWTH FROM PREVIOUS DAY
us_rev = us.iloc[::-1].positive.diff()
fig = plt.figure(figsize=(15,5))
us_rev.plot(linewidth=3, marker = 'o', markersize=10)
plt.title('Positive Case Growth')
plt.grid()

fig.savefig('images/positive_case_growth.png')

# POSITIVE CASES IN ILLINOIS
fig = plt.figure(figsize=(15,5))
states[states.state == 'IL'].positive.plot(linewidth=3, marker = 'o', markersize=10)
plt.title('Illinois Confirmed Cases')
plt.grid()

fig.savefig('images/illinois_cases.png')

# POSITIVE CASES IN NY
fig = plt.figure(figsize=(15,5))
states[states.state == 'NY'].positive.plot(linewidth=3, marker = 'o', markersize=10)
plt.title('New York Confirmed Cases')
plt.grid()

fig.savefig('images/ny_cases.png')

# POSITIVE CASES IN IA
fig = plt.figure(figsize=(15,5))
states[states.state == 'IA'].positive.plot(linewidth=3, marker = 'o', markersize=10)
plt.title('Iowa Confirmed Cases')
plt.grid()

fig.savefig('images/ia_cases.png')

# POSITIVE CASES IN HIGHEST COUNT CITIES
top_ten = today.sort_values(by='positive', ascending=False)[:10]
ten_states = top_ten.state
fig = plt.figure(figsize=(15,5))
for state in ten_states:
    if state in list(ten_states[:5].values):
        states[states.state == state].positive.plot(label = state, linewidth=3, marker = 'o', markersize=10)
    else:
        states[states.state == state].positive.plot(label = state, linewidth=1, marker = 'o', markersize=3)
plt.title('10 states with the most confirmed cases')
plt.ylabel('Positive Test Results')
plt.legend(loc='upper left')
plt.grid()

fig.savefig('images/top_ten_states.png')

# CASES BY STATE –– MAP
fig = go.Figure(data=go.Choropleth(
    locations=today.state, # Spatial coordinates
    z = today.positive, # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Confirmed Cases",
))

fig.update_layout(
    title_text = 'COVID-19 Cases by State',
    geo_scope='usa', # limite map scope to USA
)


fig.write_image('images/positive_cases_map.png')

# POSITIVE TEST RATE
today['positive_rate'] = today.positive/today.total
rates = today.sort_values(by='positive_rate', ascending = False)
rates = rates[['state', 'positive_rate', 'death', 'positive']]
rates = rates.set_index('state')
colors = [Color(pick_for=x).get_hex_l() for x in rates.index]
fig = go.Figure([go.Bar(x=rates.index, y=rates.positive_rate, marker_color=colors)])
fig.update_layout(
    title_text = 'Positive Test Rate'
)

fig.write_image('images/positive_test_rate.png')

# MORTALITY RATE
rates['death_rate'] = rates.death/rates.positive
rates = rates.sort_values(by='death_rate', ascending=False)
fig = go.Figure([go.Bar(x=rates.index, y=rates.death_rate, marker_color=colors)])
fig.update_layout(
    title_text = 'Mortality Rate')

fig.write_image('images/mortality_rate.png')

# SAVE DATA
us.reset_index(inplace = True)
states.reset_index(inplace=True)
us.date = us.date.astype(str)
states.date = states.date.astype(str)
national_data = us.to_dict()
state_data = states.to_dict()


data = {'state': state_data,
        'us': national_data}

with open('coronavirus.json', mode='w', encoding='utf-8') as f:
    json.dump(data, f)

with open('coronavirus.json') as f:
    data = json.load(f)
    state = data['state']