# Import python packages
import streamlit as st
import numpy as np
import pandas as pd
import snowflake.connector
import plotly.express as px
import streamlit.components.v1 as components

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

import os
from datetime import datetime, timedelta

# Queries
from queries import *

# Config
st.set_page_config(
    page_title="NHL Season Analysis",
    page_icon=":ice_hockey_stick_and_puck:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Write directly to the app
st.title("NHL Season Analysis  :ice_hockey_stick_and_puck:")

# Snowflake Connection
pk_str = st.secrets["snowflake"]["private_key"]
pk = serialization.load_pem_private_key(
    pk_str.encode(),
    password=None,
    backend=default_backend()
)
pk_der = pk.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    account=st.secrets["snowflake"]["account"],
    role=st.secrets["snowflake"]["role"], 
    private_key=pk_der, 
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"]
)
st.write("Connected to Snowflake!")

cur = conn.cursor()

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
    cur.execute(query)
    df = cur.fetch_pandas_all()
    return df

# Create the Stats Query and DataFrame
teams = execute_queries(teams())
stats = execute_queries(stats(input_start_date, input_end_date))
regular_season = execute_queries(regular_season(input_start_date, input_end_date))
top10 = execute_queries(team_ranks())
scoring = execute_queries(scoring()) 

team_names = [name.lower() for name in teams['TEAM'].unique()]

# Regular Season
st.subheader("Regular Season Data")
st.write("The teams that are provided are filtered from the table to narrow to games where this matchup has occurred during this year's regular season.")
st.write("*_NOTE_*: The data will appear duplicate, but each row is unique. This table combines dimensional data per team statistics that is slowly-changing. In addition, the schedule data is joined in for a full perspective.")

if st.button("Reset", type="primary"):
    st.write('Sending out the Zamboni. The prediction results will clear momentarily.')

st.subheader("Current Season Analysis")
st.write("Current Top 10 Ranking Teams by Wins vs. Losses")
fig = px.histogram(top10, x="TEAM", y=["OVERALL_WINS", "OVERALL_LOSSES", "OVERTIME_LOSSES"])
fig.update_layout(barmode='group')
st.plotly_chart(fig, key="top10teams")
scores = px.histogram(top10, x="TEAM", y=["GOALS_FOR", "GOALS_AGAINST"])
scores.update_layout(barmode='group')
st.plotly_chart(scores, key="top10teamsscoring")

st.dataframe(top10, use_container_width=True)
             

st.write("\t\t\t\tScoring Percentages by Away Goals and Home Goals")
st.write(
    "Calculated using the percentage of goals scored in favor of teams.\n",
    "- If that percentage is negative, the team has scored less than their opponents on average. \n",
    "- If zero, the team has scored equal to their opponents on average. \n",
    "- If positive, the team has scored more than their opponents on average. "
)
fig = px.bar(scoring, x="TEAM", y="SCORING_PCT")
st.plotly_chart(fig, key="scoring_percentages")
st.dataframe(scoring, use_container_width=True)

st.write("Season Schedule and Team Statistics")
st.dataframe(stats, use_container_width=True)
