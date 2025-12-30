import streamlit as st
import pandas as pd

import calendar
import time
import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine
from tabulate import tabulate
import season_queries
from datetime import datetime
import os

st.set_page_config(page_title="Mid-Atlantic Masters: Team Season Standings")


st.title("Team Season Standings")

engine = create_engine("duckdb:///md:mamasters")


with engine.connect() as connection:

  selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), index=None, placeholder="Choose a season...")

  if selected_season == None:
    st.write('No season selected.')

  else:
    last_race_date = connection.execute(text(f"""
      select max(racedate) as max_date, count(distinct racekey) as racenames from team_results where racekey in(select racename from schedule where counting_season = '{selected_season}')
      """))
    racedate = last_race_date.fetchone()
    racedatestring = racedate._mapping["max_date"]
    racecountstring = racedate._mapping["racenames"]
    schedule = connection.execute(text(f"""
      select count(*) as total_races, round(count(*)/2)::integer as scored_races from schedule where counting_season = '{selected_season}'
      """))
    schedule_details = schedule.fetchone()
    total_races = schedule_details._mapping["total_races"]

    st.markdown("#### Scoring Details")
    st.markdown(f"""
      * Standings as of {racedatestring}. There have been {racecountstring} completed races so far.
      * {selected_season} season has {total_races} races total. All races count.
      """)

    st.markdown(f"##### Teams - Overall Season Standings")

    context = {**globals(), **locals()}
    get_results_query = season_queries.q_team_season.format(**context)
    results = connection.execute(text(get_results_query))

    st.dataframe(results)

  connection.close()

engine.dispose()