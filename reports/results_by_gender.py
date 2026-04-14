import streamlit as st
import pandas as pd

import urllib.parse
from urllib.parse import urlencode
from sqlalchemy import text
from sqlalchemy import create_engine

from tabulate import tabulate
import gender_queries
import class_queries
import overall_queries
import os

def clear_params():
	st.query_params.clear()

if st.query_params:
	st.session_state.seasonkey=st.query_params["season"]
	st.session_state.racekey=st.query_params["race"]
	st.session_state.scoringkey=st.query_params["scoring"]

st.set_page_config(page_title="Mid-Atlantic Masters: Race Results (Individual)")

st.title("Race Results (Individual)")

racing_md_token =os.getenv("RACING_MD_TOKEN")

engine = create_engine("duckdb:///md:mamasters?motherduck_token={racing_md_token}")

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
	col1, col2, col3 = st.columns(3)

	with col1:
		selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), key="seasonkey", index=None, placeholder="Choose a season...", on_change=clear_params)
		st.query_params["season"]=selected_season

	with col2:
		options = connection.execute(text(f"""
			select distinct(racekey) from results_by_gender_vw where season = '{selected_season}' order by 1;
			"""))
		selected_option = st.selectbox('Race', options, key="racekey", index=None, placeholder="Choose a race...", on_change=clear_params)
		st.query_params["race"]=selected_option

	with col3:
		selected_scoring = st.selectbox('Scoring Report', ("Overall Results","Results by Gender", "Results by Class"), key="scoringkey", index=None, placeholder="Choose a scoring report...", on_change=clear_params)
		st.query_params["scoring"]=selected_scoring

	if selected_option == None:
		st.write('No race selected.')

	elif selected_scoring == "Results by Gender":
		context = {**globals(), **locals()}
		get_genders_query = gender_queries.q_get_genders.format(**context)
		genders = connection.execute(text(get_genders_query))

		for row in genders:
			with st.container():
				gender = row.gender
				gender_header=row.gender_header

				st.markdown(f"##### {gender_header} - Overall Individual Results")
				with engine.connect() as conn_inner:
					context = {**globals(), **locals()}
					get_results_query = gender_queries.q_select_results_by_gender.format(**context)
					results = conn_inner.execute(text(get_results_query))

					st.dataframe(results, hide_index=True)
					conn_inner.close()
				engine.dispose()

	elif selected_scoring == "Results by Class":
		context = {**globals(), **locals()}
		get_classes_query = class_queries.q_class_list.format(**context)
		classes = connection.execute(text(get_classes_query))

		for row in classes:
			with st.container():
				gender = row.gender
				gender_header=row.gender_header
				raceclass = row.raceclass

				st.markdown(f"##### {gender_header} Class {raceclass} Results")
				with engine.connect() as conn_inner:
					context = {**globals(), **locals()}
					get_class_results = class_queries.q_class_results.format(**context)
					results = conn_inner.execute(text(get_class_results))

					st.dataframe(results, hide_index=True)
					conn_inner.close()
				engine.dispose()

	elif selected_scoring == "Overall Results":
		context = {**globals(), **locals()}

		st.markdown(f"##### Overall Results")

		context = {**globals(), **locals()}
		get_overall_results = overall_queries.q_select_overall_results.format(**context)
		results = connection.execute(text(get_overall_results))

		st.dataframe(results, hide_index=True)

	else:
		st.write('Select a scoring report to see results from this race. Available options are overall results, results by gender, results by class.')

	connection.close()

engine.dispose()
