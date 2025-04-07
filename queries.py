import streamlit as st

def stats(start, end):
    return f"""
        SELECT * FROM NHL_STATS.RAW.SEASONAL_METRICS_AGG
        WHERE GAME_DATE BETWEEN '{start}' and '{end}'
        ORDER BY DATE DESC
    """

def teams():
    return f"""
        SELECT * FROM NHL_STATS.RAW.TEAMS
    """

def regular_season(start, end):
    return f"""
        SELECT *
        FROM NHL_STATS.RAW.GAMES
        WHERE DATE BETWEEN '{start}' and '{end}'
        ORDER BY DATE DESC
    """
    
# def predictions_overview_query(start, end, away, home):
#     return f"""
#         SELECT *
#         FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_PREDICTIONS
#         WHERE DATE BETWEEN '{start}' and '{end}'
#             AND LOWER(AWAY_TEAM_ID) LIKE ('%{away.lower()}%')
#             AND LOWER(HOME_TEAM_ID) LIKE ('%{home.lower()}%')
#         ORDER BY DATE DESC
#     """

# def predictions_full_query(start, end):
#     return f"""
#         SELECT * 
#         FROM PC_DBT_DB.NHL_SEASON_STATS_AGG.NHL_SEASON_PREDICTIONS
#         WHERE DATE BETWEEN '{start}' and '{end}'
#         ORDER BY DATE DESC
#     """
