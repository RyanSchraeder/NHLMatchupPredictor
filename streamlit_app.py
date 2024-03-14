# Import python packages
import streamlit as st
import numpy as np
import pandas as pd

import pygwalker as pyg
import streamlit.components.v1 as components

import os
from datetime import datetime, timedelta
from src.connectors import get_snowflake_connection

# Queries
from queries import stats, teams, predictions_full_query, predictions_overview_query

# Config
st.set_page_config(
    page_title="NHL Matchup Predictor",
    page_icon=":ice_hockey_stick_and_puck:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Write directly to the app
st.title("NHL Matchup Predictor :ice_hockey_stick_and_puck:")

input_away_team = st.text_input(label='Away Team:')
if not input_away_team or input_away_team == '':
    st.write("Please enter away team.")

input_home_team = st.text_input(label="Home Team:")
if not input_home_team or input_home_team == '':
    st.write("Please enter home team.")

input_start_date = st.text_input(label="Start Date (Defaults to Last 30 Days, this field is optional.)")
input_end_date = st.text_input(label="End Date (Defaults to Current Day, this field is optional.)")

# Dates set
if not input_start_date:
    input_start_date = datetime.now().date() - timedelta(days=30)

if not input_end_date:
    input_end_date = datetime.now().date()

# Get the current credentials
conn = get_snowflake_connection('standard')
cursor = conn.cursor()

# Set function to query snowflake and return DataFrame
@st.cache_data
def execute_queries(query):
    df = cursor.execute(query).fetch_pandas_all()
    return df

# Create the Stats Query and DataFrame
teams = execute_queries(teams())
stats = execute_queries(stats(input_start_date, input_end_date))
st.write("Season Schedule and Team Statistics Dataset:")
st.dataframe(stats, use_container_width=True)

# Create the Predictions Query and DataFrame
predictions = execute_queries(predictions_full_query(input_start_date, input_end_date))
predictions_overview = execute_queries(predictions_overview_query(input_start_date, input_end_date, input_away_team, input_home_team))

# Prepare data transformations for input validation
# Drop unnecessary columns from team stats
stats.drop(['HOME_TEAM', 'AWAY_TEAM', 'AWAY_SRS', 'HOME_SRS', 'AWAY_RGREC', 'HOME_RGREC'], axis=1, inplace=True)

team_names = teams['AWAY_TEAM_ID'].unique()

# Input Validation

if input_away_team not in team_names or input_home_team not in team_names:
    st.write(f"""Here's the list of teams""")
    st.write(team_names)

else: 
    st.write(f"Awesome! We got both teams ready. Looks like you're looking for {input_away_team} Vs. {input_home_team}. Click Faceoff and let the games begin! :ice_hockey_stick_and_puck:")

# Generate all information. Start with a button
if st.button('Faceoff'):
    # Regular Season
    st.subheader("Regular Season Data")
    st.write("The teams that are provided are filtered from the table to narrow to games where this matchup has occurred during this year's regular season.")
    st.write("*_NOTE_*: The data will appear duplicate, but each row is unique. This table combines dimensional data per team statistics that is slowly-changing. In addition, the schedule data is joined in for a full perspective.")
    
    # results = stats[ (stats['AWAY_TEAM_ID'] == input_away_team) & (stats['HOME_TEAM_ID'] == input_home_team) ]

    # Display the dataset to enable interactive analysis
    st.subheader("Build Your Own Analysis.")
    st.write("""
        This Tableau-like display contains a dataset consisting of regular season, playoffs, and team stats along with the predicted winners of each game.
        Use it to build your own visualizations to dive deeper into the data for all predictions.
    """)
    viz = pyg.to_html(predictions)

    # Embed the HTML into the Streamlit app
    components.html(viz, height=800, scrolling=True)

    st.subheader(f'Prediction Model Output for {input_away_team} Vs. {input_home_team}')
    st.write('''
        The predictions are appended to the season schedule based upon its input data, 
        including any future games that are not yet complete with data. From there, they're filtered down to retrieve the predicted outcomes and compared to the actual outcomes from the past matchups.
    '''
    )
    st.write(
        '_NOTE_: For future games, the goals are assumed to be 0 for each team in the matchup so the model caters toward stats.',
        ' For this reason, sometimes you may see multiple records for the same game because predictions were made based upon a varying',
        ' stat for either team given multiple records according to a stat that may have changed. For example:'
    )
    st.markdown('''
        | DATE | AWAY_TEAM_ID | AWAY_GOALS | HOME_TEAM_ID | HOME_GOALS | ACTUAL | PREDICTION | AWAY_SOS (statistic in question) | HOME_SOS (statistic in question) |
        | ---  | ----------   | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | -------- |
        | 2024-03-12 | Colorado Avalanche | 0 | Calgary Flames | 0 | Colorado Avalanche | Calgary Flames | 0 | 1 |
        | 2024-03-12 | Colorado Avalanche | 0 | Calgary Flames | 0 | Colorado Avalanche | Calgary Flames | 1 | 0 |       
                     
    ''')

    st.write("")
    st.write("Predictions:")
    st.dataframe(predictions_overview, use_container_width=True)

    # if len(predictions_overview) == 0 or not predictions_overview:
    #     st.write("It looks like those teams didn't face each other in your input time range. Try again. Here are the teams with games that occurred then:")
    #     away, home = predictions["AWAY_TEAM_ID"].unique(), predictions["HOME_TEAM_ID"].unique()
    #     st.dataframe(pd.DataFrame(away, home), use_container_width=True)

    # Filter away and home team predictions for the result statement
    away_wins = predictions_overview[predictions_overview["PREDICTION"]==input_away_team]
    home_wins = predictions_overview[predictions_overview["PREDICTION"]==input_home_team]

    if len(home_wins) > len(away_wins):
        st.write(f'Based on regular season games and stats, the model antipicates a _Home Team Victory_ for the {input_home_team} when matched with the contender.')
    elif len(home_wins) < len(away_wins):
        st.write(f'Based on regular season games and stats, the model antipicates a _Away Team Victory_ for the {input_away_team} when matched with the contender.')
else:
    st.write('Please fill out the values and click the Faceoff Button to view your NHL team matchup.')

if st.button("Reset", type="primary"):
    st.write('Sending out the Zamboni. The prediction results will clear momentarily.')

