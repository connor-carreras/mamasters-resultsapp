import streamlit as st
import pandas as pd

import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine
from datetime import datetime
import ingestion_queries
import os

st.title("Enter DSQs")

firebolt_id = os.getenv('FIREBOLT_ID')
firebolt_secret = os.getenv('FIREBOLT_SECRET')

secret = urllib.parse.quote_plus(firebolt_secret)
engine = create_engine("firebolt://" + firebolt_id + ":" + secret + "@mamasters/ingest_engine?account_name=mamasters")

insert_time = datetime.now()

with engine.connect() as connection:
	col1, col2 = st.columns(2)

	with col1:
		selected_season = st.selectbox('Season', ("2024-2025","2023-2024"), index=None, placeholder="Choose a season...")

		context = {**globals(), **locals()}
		races_list_query = ingestion_queries.q_dsq_races_list.format(**context)
		races_list = connection.execute(text(races_list_query))

	with col2:
		selected_race = st.selectbox('Race Name', races_list, index=None, placeholder="Choose a race...")

		context = {**globals(), **locals()}
		dsqs_exist = ingestion_queries.q_dsq_exists.format(**context)
		results_exist = connection.execute(text(dsqs_exist))
		resultscount = results_exist.fetchone()
		resultscountstring = resultscount._mapping["num_records"]

	if selected_race == None:
		st.write('Please select a race. You need to choose a race before you can input DSQs.')

	elif resultscountstring > 0:
		st.write('DSQs have already been entered for this race. Current DSQ entries are below:')

		context = {**globals(), **locals()}
		show_dsqs = ingestion_queries.q_show_dsqs.format(**context)
		dsq_table = connection.execute(text(show_dsqs))
		st.dataframe(dsq_table)

		st.write('If you would like to change these DSQ entries, fill out the form below and include all DSQs.')

		context = {**globals(), **locals()}
		mountains_list = ingestion_queries.q_dsq_mountain.format(**context)
		mountain = connection.execute(text(mountains_list))
		mountainname = mountain.fetchone()
		mountainstring = mountainname._mapping["mountain"]

		context = {**globals(), **locals()}
		race_dates_query = ingestion_queries.q_dsq_date.format(**context)
		unique_date = connection.execute(text(race_dates_query))
		racedate = unique_date.fetchone()
		datestring = racedate._mapping["racedate"]

		context = {**globals(), **locals()}
		race_type_query = ingestion_queries.q_dsq_type.format(**context)
		unique_type = connection.execute(text(race_type_query))
		racetype = unique_type.fetchone()
		typestring = racetype._mapping["racetype"]

		context = {**globals(), **locals()}
		names_list_query = ingestion_queries.q_dsq_names.format(**context)
		names_list = connection.execute(text(names_list_query))

		context = {**globals(), **locals()}
		names_list_query2 = ingestion_queries.q_dsq_names.format(**context)
		names_list2 = connection.execute(text(names_list_query2))

		with st.form("Enter DSQs"):
			st.write("Select the racers who had a DSQ for run 1. You can select multiple racers.")
			racers = st.multiselect("Racer names", names_list, key=1)
			st.write("Select the racers who had a DSQ for run 2. You can select multiple racers.")
			racers2 = st.multiselect("Racer names", names_list2, key=2)
			submitted = st.form_submit_button("Submit")
			if submitted:
				context = {**globals(), **locals()}
				insert_dsqs = ingestion_queries.q_dsq_insert_run1.format(**context)
				connection.execute(text(insert_dsqs))
				st.write("Run 1 DSQs uploaded.")
				context = {**globals(), **locals()}
				insert_dsqs2 = ingestion_queries.q_dsq_insert_run2.format(**context)
				connection.execute(text(insert_dsqs2))
				st.write("Run 2 DSQs uploaded.")

	else:
		context = {**globals(), **locals()}
		mountains_list = ingestion_queries.q_dsq_mountain.format(**context)
		mountain = connection.execute(text(mountains_list))
		mountainname = mountain.fetchone()
		mountainstring = mountainname._mapping["mountain"]

		context = {**globals(), **locals()}
		race_dates_query = ingestion_queries.q_dsq_date.format(**context)
		unique_date = connection.execute(text(race_dates_query))
		racedate = unique_date.fetchone()
		datestring = racedate._mapping["racedate"]

		context = {**globals(), **locals()}
		race_type_query = ingestion_queries.q_dsq_type.format(**context)
		unique_type = connection.execute(text(race_type_query))
		racetype = unique_type.fetchone()
		typestring = racetype._mapping["racetype"]

		context = {**globals(), **locals()}
		names_list_query = ingestion_queries.q_dsq_names.format(**context)
		names_list = connection.execute(text(names_list_query))

		context = {**globals(), **locals()}
		names_list_query2 = ingestion_queries.q_dsq_names.format(**context)
		names_list2 = connection.execute(text(names_list_query2))

		with st.form("Enter DSQs"):
			st.write("Select the racers who had a DSQ for run 1. You can select multiple racers.")
			racers = st.multiselect("Racer names", names_list, key=1)
			st.write("Select the racers who had a DSQ for run 2. You can select multiple racers.")
			racers2 = st.multiselect("Racer names", names_list2, key=2)
			submitted = st.form_submit_button("Submit")
			if submitted:
				context = {**globals(), **locals()}
				insert_dsqs = ingestion_queries.q_dsq_insert_run1.format(**context)
				connection.execute(text(insert_dsqs))
				st.write("Run 1 DSQs uploaded.")
				context = {**globals(), **locals()}
				insert_dsqs2 = ingestion_queries.q_dsq_insert_run2.format(**context)
				connection.execute(text(insert_dsqs2))
				st.write("Run 2 DSQs uploaded.")

	connection.close()
engine.dispose()