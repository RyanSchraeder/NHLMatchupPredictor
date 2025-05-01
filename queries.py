import streamlit as st

def stats(start, end):
    return f"""
        SELECT * FROM NHL_STATS.RAW.SEASONAL_METRICS_AGG
        WHERE GAME_DATE BETWEEN '{start}' and '{end}'
        ORDER BY GAME_DATE DESC
    """

def teams():
    return f"""
        SELECT * FROM NHL_STATS.RAW.TEAM_STATISTICS
    """
def team_ranks():
    return f"""
        WITH WIN_LOSS_RATIOS AS (
            SELECT *,
                OVERALL_WINS / (OVERALL_WINS + OVERALL_LOSSES) * 1.0 AS WIN_LOSS_RATIO
            FROM TEAM_STATISTICS
            ORDER BY WIN_LOSS_RATIO
        ), RANKS AS (
            SELECT 
                *, 
                RANK() OVER(ORDER BY WIN_LOSS_RATIO DESC) AS LEAGUE_RANK
            FROM WIN_LOSS_RATIOS
        )
        SELECT * 
        FROM RANKS 
        WHERE LEAGUE_RANK <= 10
        ORDER BY LEAGUE_RANK 
        ;
    """
def scoring():
    return f"""
        WITH AWAY_SCORING AS (
            SELECT 
                VISITOR,  
                SUM(VISITOR_GOALS) AS SCORED_FOR, 
                SUM(HOME_GOALS) AS SCORED_AGAINST
            FROM NHL_STATS.RAW.SEASONAL_METRICS_AGG
            GROUP BY 1
        ), HOME_SCORING AS (
            SELECT 
                HOME,  
                SUM(HOME_GOALS) AS SCORED_FOR, 
                SUM(VISITOR_GOALS) AS SCORED_AGAINST
            FROM NHL_STATS.RAW.SEASONAL_METRICS_AGG
            GROUP BY 1
        ), GROUPED AS (
            SELECT 
                A.VISITOR AS TEAM, 
                A.SCORED_FOR AS AWAY_GOALS_FOR, 
                A.SCORED_AGAINST AS AWAY_GOALS_AGAINST, 
                B.SCORED_FOR AS HOME_GOALS_FOR, 
                B.SCORED_AGAINST AS HOME_GOALS_AGAINST
            FROM AWAY_SCORING A
            JOIN HOME_SCORING B
            ON A.VISITOR = B.HOME
        )
        SELECT 
            TEAM, 
            ROUND( ((AWAY_GOALS_FOR + HOME_GOALS_FOR) / (AWAY_GOALS_AGAINST + HOME_GOALS_AGAINST) - 1.0) * 100, 2 ) AS SCORING_PCT,
            DENSE_RANK() OVER(ORDER BY SCORING_PCT DESC) SCORING_RANK
        FROM GROUPED 
    """
    
def regular_season(start, end):
    return f"""
        SELECT *
        FROM NHL_STATS.RAW.GAMES
        WHERE GAME_DATE BETWEEN '{start}' and '{end}'
        ORDER BY GAME_DATE DESC
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
