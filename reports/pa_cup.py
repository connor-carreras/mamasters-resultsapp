import streamlit as st
import pandas as pd

import calendar
import time
import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine
from tabulate import tabulate
import pacup_queries
from datetime import datetime
import os

st.set_page_config(page_title="Mid-Atlantic Masters: Pennsylvania Cup Standings")


st.title("Pennsylvania Cup Standings")

racing_md_token =os.getenv("RACING_MD_TOKEN")

engine = create_engine("duckdb:///md:mamasters?motherduck_token={racing_md_token}")

with st.expander("ℹ️ Understand Pennsylvania Cup scoring"):
  st.markdown("""
    **Calculating Pennsylvania Cup scoring**
    1. To qualify for Pennsylvania Cup scoring, you must participate in all races designated as part of the Pennsylvania Cup mini-series.
    2. Based on results from the first race in the series, racers are grouped into four ability classes: Female Super Elite, Female Elite, Male Super Elite, Male Elite.
    3. Racers earn old world cup points based on their finish position within their ability class. See the table below for details about old world cup points.
    4. The total number of world cup points accumulated over the entire Pennsylvania Cup determine each racer's position within their ability class.
    5. DNFs and DSQs receive 0 world cup points.

    **Old World Cup Scoring Table**
    | Place: Points |
    | -------- |
    | 1st place: 25 points |
    | 2nd place: 20 points |
    | 3rd place: 15 points |
    | 4th place: 12 points |
    | 5th place: 11 points |
    | 6th place: 10 points |
    | 7th place: 9 points |
    | 8th place: 8 points |
    | 9th place: 7 points |
    | 10th place: 6 points |
    | 11th place: 5 points |
    | 12th place: 4 points |
    | 13th place: 3 points |
    | 14th place: 2 points |
    | 15th place: 1 points |
  """)

with engine.connect() as connection:

  selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), index=None, placeholder="Choose a season...")

  if selected_season == None:
    st.write('No season selected.')

  else:
    context = {**globals(), **locals()}
    get_classes_query = pacup_queries.q_class_list.format(**context)
    classes = connection.execute(text(get_classes_query))


    for row in classes:
        with st.container():
          gender = row.gender
          gender_header=row.gender_header
          ability_class = row.ability_class

          st.markdown(f"##### {gender_header} {ability_class} Results")
          with engine.connect() as conn_inner:
            context = {**globals(), **locals()}
            get_results_query = pacup_queries.q_pa_cup_2025.format(**context)
            results = conn_inner.execute(text(get_results_query))

            st.dataframe(results, hide_index=True)
            conn_inner.close()
          engine.dispose()

  connection.close()

engine.dispose()