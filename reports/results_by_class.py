import streamlit as st
import pandas as pd

import urllib.parse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from tabulate import tabulate
import class_queries
import os

st.title("Race Results by Class")

firebolt_id = os.getenv('FIREBOLT_ID')
firebolt_secret = os.getenv('FIREBOLT_SECRET')

secret = urllib.parse.quote_plus(firebolt_secret)
engine = create_engine("firebolt://" + firebolt_id + ":" + secret + "@mamasters/ingest_engine?account_name=mamasters")

with engine.connect() as connection:

	col1, col2 = st.columns(2)

	with col1:
		selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), index=None, placeholder="Choose a season...")

	with col2:
		options = connection.execute(text(f"""
		select distinct(racekey) from results_by_class_vw where season = '{selected_season}' order by 1;
		"""))
		selected_option = st.selectbox('Race', options, index=None, placeholder="Choose a race...")

	context = {**globals(), **locals()}
	get_classes_query = class_queries.q_class_list.format(**context)
	classes = connection.execute(text(get_classes_query))


###Generate Visuals
	for row in classes:
		with st.container():
			gender = row.gender
			gender_header=row.gender_header
			raceclass = row.raceclass

			st.markdown(f"##### {gender_header} Class {raceclass} Results")

			context = {**globals(), **locals()}
			get_class_results = class_queries.q_class_results.format(**context)
			results = connection.execute(text(get_class_results))

			st.dataframe(results)

	connection.close()

engine.dispose()
