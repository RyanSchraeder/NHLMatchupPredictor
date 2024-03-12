# Import python packages
import streamlit as st
import numpy as np
import pandas as pd

import os
from datetime import datetime, timedelta
from src.connectors import get_snowflake_connection

# Write directly to the app
st.title("NHL Matchup Predictor :ice_hockey_stick_and_puck:")
input_away_team = st.text_input(label='Away Team:')
input_home_team = st.text_input(label="Home Team:")
input_start_date = st.text_input(label="Start Date (Defaults to Last 30 Days)")
input_end_date = st.text_input(label="End Date (Defaults to Yesterday)")

if not input_start_date:
    input_start_date = datetime.now().date() - timedelta(days=30)

if not input_end_date:
    input_end_date = datetime.now().date() - timedelta(days=1)
    
# Get the current credentials
session = get_snowflake_connection('spark')

#  Create an example dataframe
#  Note: this is just some dummy data, but you can easily connect to your Snowflake data
#  It is also possible to query data using raw SQL using session.sql() e.g. session.sql("select * from table")

query = f"""
    SELECT DISTINCT * FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_STATS 
    WHERE 
        AWAY_GOALS IS NOT NULL OR HOME_GOALS IS NOT NULL
        AND DATE BETWEEN '{input_start_date}' and '{input_end_date}'
    ORDER BY DATE DESC
  """

# st.write(query)
created_dataframe = session.sql(query)


# Execute the query and convert it into a Pandas dataframe
queried_data = created_dataframe.to_pandas()
predictions = session.sql('''SELECT * FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_STATS_PREDICTIONS ''').to_pandas()

# Close snowpark session
session.close()

# Drop unnecessary columns
queried_data.drop(['HOME_TEAM', 'AWAY_TEAM', 'AWAY_SRS', 'HOME_SRS', 'AWAY_RGREC', 'HOME_RGREC'], axis=1, inplace=True)

compare = pd.DataFrame(queried_data['AWAY_TEAM_ID'].unique(), predictions['AWAY_TEAM_ID'].unique())[0].to_dict()

# Input validation

if not input_away_team:
    st.write("Please enter away team.")
else:
    if input_away_team not in compare.values():
        st.write(f"""Looks like what you typed isn't in the list of NHL teams: {input_away_team}""")
        st.write(f"""You might want to check the list of teams:""")
        st.write(compare)
    
if not input_home_team:
    st.write("Please enter home team.")
else:  
    if input_home_team not in compare.values():
        st.write(f"""Looks like what you typed isn't in the list of NHL teams: {input_home_team}\n""")
        st.write(f"""You might want to check the list of teams:""")
        st.write(compare)

if input_away_team == input_home_team:
    st.subheader("Uh. One team can't face itself unless you are playing Quantum Hockey in a multidimensional league. :alien:")

# Regular Season
st.subheader("Regular Season Data")
st.write("The teams that are provided are filtered from the table to narrow to games where this matchup has occurred during this year's regular season.")

results = queried_data[ (queried_data['AWAY_TEAM_ID'] == input_away_team) & (queried_data['HOME_TEAM_ID']== input_home_team) ]
st.dataframe(results, use_container_width=True)

# Predictions
st.subheader('The Prediction Model Results')
st.write('''
    The predictions are appended to the season schedule based upon its input data, 
    including any future games that are not yet complete with data. From there, they're filtered down to retrieve the predicted outcomes and compared to the actual outcomes from the past matchups.
'''
)

predictions['AWAY_TEAM_ID'], predictions['HOME_TEAM_ID'], predictions["OUTCOME"], predictions["PREDICTION"] = predictions['AWAY_TEAM_ID'].replace(compare), predictions['HOME_TEAM_ID'].replace(compare), predictions["OUTCOME"].replace(compare), predictions["PREDICTION"].replace(compare)
predictions = predictions[ (predictions['AWAY_TEAM_ID'] == input_away_team) & (predictions['HOME_TEAM_ID'] == input_home_team) ]

away_wins = predictions[predictions["PREDICTION"]==input_away_team]
home_wins = predictions[predictions["PREDICTION"]==input_home_team]

if len(home_wins) > len(away_wins):
    st.write(f'Based on regular season games and stats, the model antipicates a _Home Team Victory_ for the {input_home_team} when matched with the contender.')
elif len(home_wins) < len(away_wins):
    st.write(f'Based on regular season games and stats, the model antipicates a _Away Team Victory_ for the {input_away_team} when matched with the contender.')
else:
    st.write(f'Based on regular season games and stats, the model antipicates a _Draw_ ')
  
