# Import python packages
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

import pygwalker as pyg
import streamlit.components.v1 as components

import os
from datetime import datetime, timedelta

# Queries
from queries import *

# Snowflake Connection
conn = st.connection("snowflake")

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
input_end_date = st.text_input(label="End Date (Defaults to Current Day, this field is optional. Can be up to 30 days into the future as well.)")

# Dates set
if not input_start_date:
    input_start_date = datetime.now().date() - timedelta(days=30)

if not input_end_date:
    input_end_date = datetime.now().date()


# Set function to query snowflake and return DataFrame
@st.cache_data
def execute_queries(query):
    df = conn.query(query, show_spinner=True)
    return df

# Create the Stats Query and DataFrame
teams = execute_queries(teams())
stats = execute_queries(stats(input_start_date, input_end_date))
regular_season = execute_queries(regular_season(input_start_date, input_end_date))
top5 = execute_queries(team_ranks())
scoring = execute_queries(scoring()) 

# Create the Predictions Query and DataFrame
# predictions = execute_queries(predictions_full_query(input_start_date, input_end_date))
# predictions_overview = execute_queries(predictions_overview_query(input_start_date, input_end_date, input_away_team, input_home_team))

# Prepare data transformations for input validation
# Drop unnecessary columns from team stats
# stats.drop(['HOME_TEAM', 'AWAY_TEAM', 'AWAY_SRS', 'HOME_SRS', 'AWAY_RGREC', 'HOME_RGREC'], axis=1, inplace=True)

team_names = [name.lower() for name in teams['TEAM'].unique()]

# Input Validation

if input_away_team.lower() not in team_names or input_home_team.lower() not in team_names:
    if not len(input_away_team) or not len(input_home_team):
        pass
    else:
        st.write(f"""We couldn't find the teams you've entered. Here's the list of teams: """)
        st.write(team_names)

else: 
    st.write(f"Awesome! We got both teams ready. Looks like you're looking for {input_away_team} Vs. {input_home_team}. Click Faceoff and let the games begin! :ice_hockey_stick_and_puck:")

# Generate all information. Start with a button
if st.button('Faceoff'):

    # st.subheader(f'Prediction Model Output for {input_away_team} Vs. {input_home_team}')

    # st.dataframe(predictions_overview, use_container_width=True)
    # res = {k: v for k, v in predictions_overview.to_dict().items()}
    # if res["BAD_PREDICTION_FLAG"] == 1:
    #     st.write("Sorry about that! It looks like the model went out of the way on this one. :|")

    # Regular Season
    st.subheader("Regular Season Data")
    st.write("The teams that are provided are filtered from the table to narrow to games where this matchup has occurred during this year's regular season.")
    st.write("*_NOTE_*: The data will appear duplicate, but each row is unique. This table combines dimensional data per team statistics that is slowly-changing. In addition, the schedule data is joined in for a full perspective.")

    # Display the dataset to enable interactive analysis
    st.subheader("Explore the Data")
    st.write("""
        This Tableau-like display contains a dataset consisting of regular season, playoffs, and team stats along with the predicted winners of each game.
        Use it to build your own visualizations to dive deeper into the data for all predictions.
    """)
    viz = pyg.to_html(regular_season)

    # Embed the HTML into the Streamlit app
    components.html(viz, height=800, scrolling=True)


    # if not len(predictions_overview):
    #     st.write("It looks like those teams didn't face each other in your input time range. Try again. Here are the teams with games that occurred then:")
    #     away, home = predictions["AWAY_TEAM_ID"].unique(), predictions["HOME_TEAM_ID"].unique()
    #     st.dataframe(pd.DataFrame(away, home), use_container_width=True)
        
else:
    st.write('Please fill out the values and click the Faceoff Button to view your NHL team matchup.')

if st.button("Reset", type="primary"):
    st.write('Sending out the Zamboni. The prediction results will clear momentarily.')

st.subheader("Current Season Analysis")
st.write("Current Top 5 Ranks by Wins vs. Losses")
rank_chart = alt.Chart(top5).mark_bar().encode(
    x='OVERALL_WINS',
    y=alt.Y('TEAM').sort('-x'),
    color='OVERALL_LOSSES'
).interactive()

# Use the native Altair theme.
st.altair_chart(rank_chart, theme=None, use_container_width=True)

st.write("\t\t\t\tScoring Percentages by Away Goals and Home Goals")
st.write(
    "Calculated using the percentage of goals scored in favor of teams.\n",
    "- If that percentage is negative, the team has scored less than their opponents on average. \n",
    "- If zero, the team has scored equal to their opponents on average. \n",
    "- If positive, the team has scored more than their opponents on average. "
)
scoring = alt.Chart(scoring).mark_bar().encode(
    x='TEAM',
    y=alt.Y('SCORING_PCT').sort('-x'),
    color='SCORING_RANK'
).interactive()

# Use the native Altair theme.
st.altair_chart(scoring, theme=None, use_container_width=True)

st.write("Season Schedule and Team Statistics")
st.dataframe(stats, use_container_width=True)

# Display Model Evaluation
# model_stats = execute_queries("SELECT * FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_PREDICTOR_SCORING;")
# st.subheader("Current Prediction Model Evaluation Metrics")
# st.write(f"Upon test data with a sample size of 30%, the model predicts the winner correctly {round(model_stats['accuracy'].mean() * 100, 2)}% often.")
# st.write("Instead of predicting win or loss in favor of one team, both sides are evaluated and the probability of each team winning given the matchup is calculated. If a team's probability of winning is greater than 50%, the model will label that team the winner.")
# st.dataframe(model_stats)
