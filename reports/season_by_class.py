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

st.set_page_config(page_title="Mid-Atlantic Masters: Season Standings by Class")


st.title("Season Standings by Class")

racing_md_token =os.getenv("RACING_MD_TOKEN")

engine = create_engine("duckdb:///md:mamasters?motherduck_token={racing_md_token}")

with st.expander("ℹ️ Understand seasonal scoring by class"):
  st.markdown("""
    **Calculating Seasonal Standings by Class**
    1. Only Mid-Atlantic members can qualify for overall season awards. You can [purchase a membership](https://masters.adminskiracing.com/node/402199) up until the last race weekend of the season to become eligible for seasonal scoring.
    2. A racer's class is determined by their age on January 1 of the race season. For example, a racer born in September 1991 will be 33 on January 1, 2025, which will put that racer in Class 2 for the 2024-2025 race season.
    3. If a racer moves up in class between seasons, any points scored in their previous class for any counting races for the current season will carry over to the current season. 
    For example: A racer scores 80 world cup points in class 4 during a race held after the Mid-Atlantic seasonal finals during the 2023-2024 season (which means that the race counts towards seasonal scoring for the 2024-2025 season). For the 2024-2025 season, that racer moves up to class 5. 
    The racer's 80 points will carry over to his 2024-2025 seasonal scoring. Points will not be retroactively re-calculated for any racers who move to a new class.
    4. An individual racer must have at least 6 starts to qualify for overall season awards.
    5. Mid-ATL uses World Cup scoring down to 30th place (see table below for details). Points are awarded for position in 5-year age class, per race. 
    6. Standings are calculated by taking the best N scores for each racer and adding the total number of world cup points awarded across those N races. "N" is determined at the beginning of each season by dividing the total number of races in half and rounding up to the nearest whole number.

    **World Cup Scoring Table**
    | Place: Points | Place: Points |
    | -------- | -------|
    | 1st place: 100 points | 16th place: 15 points |
    | 2nd place: 80 points | 17th place: 14 points |
    | 3rd place: 60 points | 18th place: 13 points |
    | 4th place: 50 points | 19th place: 12 points |
    | 5th place: 45 points | 20th place: 11 points |
    | 6th place: 40 points | 21st place: 10 points |
    | 7th place: 36 points | 22nd place: 9 points |
    | 8th place: 32 points | 23rd place: 8 points |
    | 9th place: 29 points | 24th place: 7 points |
    | 10th place: 26 points | 25th place: 6 points |
    | 11th place: 24 points | 26th place: 5 points |
    | 12th place: 22 points | 27th place: 4 points |
    | 13th place: 20 points | 28th place: 3 points |
    | 14th place: 18 points | 29th place: 2 points |
    | 15th place: 16 points | 30th place: 1 point |
  """)

with engine.connect() as connection:

  selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), index=None, placeholder="Choose a season...")

  if selected_season == None:
    st.write('No season selected.')

  else:
    last_race_date = connection.execute(text(f"""
      select max(racedate) as max_date, count(distinct racekey) as racenames from results_vw where racekey in(select racename from schedule where counting_season = '{selected_season}');
      """))
    racedate = last_race_date.fetchone()
    racedatestring = racedate._mapping["max_date"]
    racecountstring = racedate._mapping["racenames"]
    schedule = connection.execute(text(f"""
      select count(*) as total_races, round(count(*)/2)::integer as scored_races from schedule where counting_season = '{selected_season}'
      """))
    schedule_details = schedule.fetchone()
    total_races = schedule_details._mapping["total_races"]
    scored_races = schedule_details._mapping["scored_races"]

    st.markdown("#### Scoring Details")
    st.markdown(f"""
      * Standings as of {racedatestring}. There have been {racecountstring} completed races so far.
      * Minimum 6 races required to qualify for season scoring.  
      * {selected_season} season has {total_races} races total. Best {scored_races} finishes count.
      """)

    tab1, tab2 = st.tabs(["Summary","Details"])

    with tab1:

      context = {**globals(), **locals()}
      get_class_query2 = season_queries.q_class_list.format(**context)
      classes2 = connection.execute(text(get_class_query2))

      for row in classes2:
            with st.container():
              gender = row.gender
              gender_header=row.gender_header
              raceclass = row.raceclass

              st.markdown(f"##### {gender_header} Class {raceclass} - Overall Season Standings")

              on = st.toggle("Show members only", key=row)
              with engine.connect() as conn_inner:
                if on:
                  context = {**globals(), **locals()}
                  get_results_query = season_queries.md_season_by_class_members.format(**context)
                  results = conn_inner.execute(text(get_results_query))

                  st.dataframe(results, hide_index=True)

                else:
                  context = {**globals(), **locals()}
                  get_results_query2 = season_queries.md_season_by_class.format(**context)
                  results2 = conn_inner.execute(text(get_results_query2))

                  st.dataframe(results2, hide_index=True)
                conn_inner.close()
              engine.dispose()

    with tab2:

      context = {**globals(), **locals()}
      get_class_query2 = season_queries.q_class_list.format(**context)
      classes2 = connection.execute(text(get_class_query2))

      for row in classes2:
            with st.container():
              gender = row.gender
              gender_header=row.gender_header
              raceclass = row.raceclass
              keyid="2"+gender+str(raceclass)

              st.markdown(f"##### {gender_header} Class {raceclass} - Overall Season Standings")

              on = st.toggle("Show members only", key=keyid)
              with engine.connect() as conn_inner:
                if on:
                  context = {**globals(), **locals()}
                  get_results_query = season_queries.md_season_by_class_details_members.format(**context)
                  results = conn_inner.execute(text(get_results_query))

                  st.dataframe(results, hide_index=True)

                else:

                  context = {**globals(), **locals()}
                  get_results_query2 = season_queries.md_season_by_class_details.format(**context)
                  results2 = conn_inner.execute(text(get_results_query2))

                  st.dataframe(results2, hide_index=True)
                conn_inner.close()
              engine.dispose()

  connection.close()

engine.dispose()