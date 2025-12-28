import streamlit as st
import pandas as pd

import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine

from tabulate import tabulate
import gender_queries
import os

st.title("Race Results by Gender")

firebolt_id = os.getenv('FIREBOLT_ID')
firebolt_secret = os.getenv('FIREBOLT_SECRET')

secret = urllib.parse.quote_plus(firebolt_secret)
engine = create_engine("firebolt://" + firebolt_id + ":" + secret + "@mamasters/ingest_engine?account_name=mamasters")

with st.expander("ℹ️ Understand race points and world cup points"):
	st.markdown("""
		**Race Points**

		Race points (also known as FIS points or USSA points) are a time-based scoring value which attempts to produce a normalized rating of a competitor's result in a race. 
		Race points provide the basis for ranking competitors across multiple races and locations. 
		The formula for computing race points is based on how close the competitor was to the winner of the race, adjusted by a factor which normalizes times across different disciplines to try to scale results to a common ranking system.

		The race point formula is defined in the FIS International Competition Rules as ((competitor's time / winner's time) - 1) * discipline adjustment factor.

		**World Cup Points**
		
		The world cup scoring system awards points to the top 30 finishers in a race. Points are allocated as shown in the table below.
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
	col1, col2 = st.columns(2)

	with col1:
		selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), index=None, placeholder="Choose a season...")

	with col2:
		options = connection.execute(text(f"""
			select distinct(racekey) from results_by_gender_vw where season = '{selected_season}' order by 1;
			"""))
		selected_option = st.selectbox('Race', options, index=None, placeholder="Choose a race...")

	if selected_option == None:
		st.write('No race selected.')

	else:
		context = {**globals(), **locals()}
		get_genders_query = gender_queries.q_get_genders.format(**context)
		genders = connection.execute(text(get_genders_query))

		for row in genders:
			with st.container():
				gender = row.gender
				gender_header=row.gender_header

				st.markdown(f"##### {gender_header} - Overall Individual Results")

				context = {**globals(), **locals()}
				get_results_query = gender_queries.q_select_results_by_gender.format(**context)
				results = connection.execute(text(get_results_query))

				st.dataframe(results)

	connection.close()

engine.dispose()
