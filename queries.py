import streamlit as st

def stats(start, end):
    return f"""
        SELECT DISTINCT * FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_STATS 
        WHERE DATE BETWEEN '{start}' and '{end}'
        ORDER BY DATE DESC
    """

def teams():
    return f"""
        SELECT DISTINCT AWAY_TEAM_ID FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_STATS
    """

def regular_season(start, end):
    return f"""
        SELECT DISTINCT 
            DATE, 
            AWAY_TEAM_ID, 
            AWAY_GOALS,
            HOME_TEAM_ID,
            HOME_GOALS,
            LENGTH_OF_GAME_MIN,
            CASE WHEN 
                HOME_GOALS = AWAY_GOALS AND HOME_GOALS = 0 AND AWAY_GOALS = 0
                THEN 'UNKNOWN' ELSE OUTCOME END AS ACTUAL, 
            PREDICTION
        FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_STATS_PREDICTIONS 
        WHERE DATE BETWEEN '{start}' and '{end}'
        ORDER BY DATE DESC
    """
    
def predictions_overview_query(start, end, away, home):
    return f"""
        SELECT *
        FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_PREDICTIONS
        WHERE DATE BETWEEN '{start}' and '{end}'
            AND LOWER(AWAY_TEAM_ID) LIKE ('%{away.lower()}%')
            AND LOWER(HOME_TEAM_ID) LIKE ('%{home.lower()}%')
        ORDER BY DATE DESC
    """

def predictions_full_query(start, end):
    return f"""
        SELECT * 
        FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_PREDICTIONS
        WHERE DATE BETWEEN '{start}' and '{end}'
        ORDER BY DATE DESC
    """
