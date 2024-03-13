# Import python packages
import streamlit as st
import numpy as np
import pandas as pd

import pygwalker as pyg
import streamlit.components.v1 as components

import os
from datetime import datetime, timedelta
from src.connectors import get_snowflake_connection

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
input_home_team = st.text_input(label="Home Team:")
input_start_date = st.text_input(label="Start Date (Defaults to Last 30 Days, this field is optional.)")
input_end_date = st.text_input(label="End Date (Defaults to Current Day, this field is optional.)")

# Dates set
if not input_start_date:
    input_start_date = datetime.now().date() - timedelta(days=30)

if not input_end_date:
    input_end_date = datetime.now().date()

# Get the current credentials
session = get_snowflake_connection('standard')
cursor = session.cursor()

# Create the Stats Query and DataFrame
stats = f"""
    SELECT DISTINCT * FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_STATS 
    WHERE DATE BETWEEN '{input_start_date}' and '{input_end_date}'
    ORDER BY DATE DESC
  """
teams = f"""SELECT DISTINCT AWAY_TEAM_ID FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_STATS"""

# Execute the query and convert it into a Pandas dataframe
cursor.execute(stats)
df = cursor.fetch_pandas_all()

cursor.execute(teams)
teams = cursor.fetch_pandas_all()

# Create the Predictions Query and DataFrame
preds = '''
    SELECT * FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_STATS_PREDICTIONS 
'''

# Execute the query and convert it into a Pandas dataframe
cursor.execute(preds)
predictions = cursor.fetch_pandas_all()

# Close session
session.close()

# Prepare data transformations for input validation
# Drop unnecessary columns
df.drop(['HOME_TEAM', 'AWAY_TEAM', 'AWAY_SRS', 'HOME_SRS', 'AWAY_RGREC', 'HOME_RGREC'], axis=1, inplace=True)
st.subheader("Analyze All Regular Season and Team Statistics on Your Own! :smile:")
analysis = pyg.to_html(df)

# Embed the HTML into the Streamlit app
components.html(analysis, height=800, scrolling=True)

team_names, team_codes = teams['AWAY_TEAM_ID'].unique(), predictions['AWAY_TEAM_ID'].unique()

compare = pd.DataFrame(team_names, team_codes)[0].to_dict()


# Input Validation

if not input_away_team:
    st.write("Please enter away team.")
else:
    if input_away_team not in compare.values():
        st.write(f"""Looks like what you typed isn't in the list of NHL teams: {input_away_team}""")
        st.write(f"""You might want to check the list of teams:""")
        st.write(compare)

    if input_away_team == input_home_team:
        st.subheader(
            "Uh. One team can't face itself unless you are playing Quantum Hockey in a multidimensional league. :alien:")

if not input_home_team:
    st.write("Please enter home team.")
else:
    if input_home_team not in compare.values():
        st.write(f"""Looks like what you typed isn't in the list of NHL teams: {input_home_team}\n""")
        st.write(f"""You might want to check the list of teams:""")
        st.write(compare)

    if input_away_team == input_home_team:
        st.subheader(
            "Uh. One team can't face itself unless you are playing Quantum Hockey in a multidimensional league. :alien:")

if len(input_away_team) > 0 and len(input_away_team) > 0:
    st.write(f"Awesome! We got both teams ready. Looks like you're looking for {input_away_team} Vs. {input_home_team}. Click Faceoff and let the games begin! :ice_hockey_stick_and_puck:")

# Generate all information. Start with a button
if st.button('Faceoff'):
    # Regular Season
    # st.subheader("Regular Season Data")
    st.write("The teams that are provided are filtered from the table to narrow to games where this matchup has occurred during this year's regular season.")

    st.write("NOTE: The data will appear duplicate, but each row is unique. This table combines dimensional data per team statistics that is slowly-changing. In addition, the schedule data is joined in for a full perspective.")

    st.write("Getting data from Snowflake...")
    st.code(stats, language="sql")
    results = df[ (df['AWAY_TEAM_ID'] == input_away_team) & (df['HOME_TEAM_ID'] == input_home_team) ]
    st.dataframe(results)

    # Predictions
    st.subheader('The Prediction Model Results')
    st.write('''
        The predictions are appended to the season schedule based upon its input data, 
        including any future games that are not yet complete with data. From there, they're filtered down to retrieve the predicted outcomes and compared to the actual outcomes from the past matchups.
    '''
    )

    st.write("Getting data from Snowflake...")
    st.code(preds, language="sql")
    predictions['AWAY_TEAM_ID'], predictions['HOME_TEAM_ID'], predictions["OUTCOME"], predictions["PREDICTION"] = predictions['AWAY_TEAM_ID'].replace(compare), predictions['HOME_TEAM_ID'].replace(compare), predictions["OUTCOME"].replace(compare), predictions["PREDICTION"].replace(compare)
    predictions = predictions[ (predictions['AWAY_TEAM_ID'] == input_away_team) & (predictions['HOME_TEAM_ID'] == input_home_team) ]

    away_wins = predictions[predictions["PREDICTION"]==input_away_team]
    home_wins = predictions[predictions["PREDICTION"]==input_home_team]

    st.write('*Summary*')
    st.dataframe(predictions)

    st.write('Prediction Model Output')
    predictions_df = predictions[['DATE', 'AWAY_TEAM_ID', 'HOME_TEAM_ID', 'PREDICTION']]
    st.dataframe(predictions_df)

    if len(home_wins) > len(away_wins):
        st.write(f'Based on regular season games and stats, the model antipicates a _Home Team Victory_ for the {input_home_team} when matched with the contender.')
    elif len(home_wins) < len(away_wins):
        st.write(f'Based on regular season games and stats, the model antipicates a _Away Team Victory_ for the {input_away_team} when matched with the contender.')
    else:
        st.write(f'Based on regular season games and stats, the model antipicates a _Draw_ ')
else:
    st.write('Please fill out the values and click the Faceoff Button to view your NHL team matchup.')

st.button("Reset", type="primary")
