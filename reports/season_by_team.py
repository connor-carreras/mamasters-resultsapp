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

st.title("Team Results")

firebolt_id = os.getenv('FIREBOLT_ID')
firebolt_secret = os.getenv('FIREBOLT_SECRET')

secret = urllib.parse.quote_plus(firebolt_secret)
engine = create_engine("firebolt://" + firebolt_id + ":" + secret + "@mamasters/ingest_engine?account_name=mamasters")


with engine.connect() as connection:

  selected_season = st.selectbox('Season', ("2024-2025"), index=None, placeholder="Choose a season...")

  if selected_season == None:
    st.write('No season selected.')

  else:
    last_race_date = connection.execute(text(f"""
      select max(racedate) as max_date, count(distinct racekey) as racenames from team_results where season = '{selected_season}'
      """))
    racedate = last_race_date.fetchone()
    racedatestring = racedate._mapping["max_date"]
    racecountstring = racedate._mapping["racenames"]

    st.markdown("#### Scoring Details")
    st.markdown(f"""
      * Standings as of {racedatestring}. There have been {racecountstring} completed races so far.
      * 2024-2025 season has 24 races total. All races count.
      """)

    st.markdown(f"##### Teams - Overall Season Standings")

    context = {**globals(), **locals()}
    get_results_query = season_queries.q_team_season.format(**context)
    results = connection.execute(text(get_results_query))

    st.dataframe(results)

  connection.close()

engine.dispose()