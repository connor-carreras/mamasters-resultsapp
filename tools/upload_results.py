import streamlit as st
import pandas as pd
import setuptools

import asyncio
import boto3
import xmltodict
import json
import calendar
import time
import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine
import ingestion_queries
import os

st.title("Upload Race Results")

st.markdown("Use this page to upload the results from the most recent race. Once you have successfully uploaded the race XML file, use the other tabs to calculate team scores and season standings.")

aws_key = os.getenv("AWS_KEY")
aws_secret =os.getenv("AWS_SECRET")
firebolt_id = os.getenv('FIREBOLT_ID')
firebolt_secret = os.getenv('FIREBOLT_SECRET')

secret = urllib.parse.quote_plus(firebolt_secret)
engine = create_engine("firebolt://" + firebolt_id + ":" + secret + "@mamasters/ingest_engine?account_name=mamasters")

with engine.connect() as connection:

	col1, col2, col3 = st.columns(3)

	with col1:
		selected_season = st.selectbox('Season', ("2024-2025","2023-2024"), index=None, placeholder="Choose a season...")
		
		context = {**globals(), **locals()}
		races_list_query = ingestion_queries.q_races_list.format(**context)
		races_list = connection.execute(text(races_list_query))

	with col2:
		selected_race = st.selectbox('Race Name', races_list, index=None, placeholder="Choose a race...")

	with col3:
		software_options = ["Split Second", "Vola"]
		software_selection = st.segmented_control(
			"Timing Software", software_options, selection_mode="single"
		)

	if selected_race != None and software_selection == 'Split Second':
		# upload file
		uploaded_file = st.file_uploader("Upload the NATFis XML file", type=["xml"])

		if uploaded_file is not None:
			today = calendar.timegm(time.gmtime())
			name = "race-results/results_" + str(today) + ".json"
			xml = uploaded_file.read()
			json_data = json.dumps(xmltodict.parse(xml))


			s3 = boto3.client(
			service_name="s3",
			region_name="us-east-1",
			aws_access_key_id=aws_key,
			aws_secret_access_key=aws_secret,
			)

			bucket_name = "mamasters-results"
			s3.put_object(
			Body=str(json_data),
			Bucket=bucket_name,
			Key=name
			)
			st.write("File successfully uploaded!")

			context = {**globals(), **locals()}
			insert_results_query = ingestion_queries.q_insert_results.format(**context)
			connection.execute(text(insert_results_query))
			
			st.write("Results table has been refreshed!")

			st.markdown("#### Preview of raw results data:")
			context = {**globals(), **locals()}
			show_results_query = ingestion_queries.q_show_results.format(**context)
			results = connection.execute(text(show_results_query))

			st.dataframe(results)

	if selected_race != None and software_selection == 'Vola':
		# upload file
		uploaded_file = st.file_uploader("Upload the Vola exported XML file", type=["xml"])

		if uploaded_file is not None:
			today = calendar.timegm(time.gmtime())
			name = "race-results/vola_" + str(today) + ".json"
			xml = uploaded_file.read()
			json_data = json.dumps(xmltodict.parse(xml))


			s3 = boto3.client(
			service_name="s3",
			region_name="us-east-1",
			aws_access_key_id=aws_key,
			aws_secret_access_key=aws_secret,
			)

			bucket_name = "mamasters-results"
			s3.put_object(
			Body=str(json_data),
			Bucket=bucket_name,
			Key=name
			)
			st.write("File successfully uploaded!")

			context = {**globals(), **locals()}
			insert_vola_query = ingestion_queries.q_insert_vola_temp.format(**context)
			connection.execute(text(insert_vola_query))

			context = {**globals(), **locals()}
			insert_results_query = ingestion_queries.q_insert_vola_to_results.format(**context)
			connection.execute(text(insert_results_query))

			context = {**globals(), **locals()}
			connection.execute(text(f"""
				truncate table vola_results_temp
				"""))
			st.write("Results table has been refreshed!")

			st.markdown("#### Preview of raw results data:")
			context = {**globals(), **locals()}
			show_results_query = ingestion_queries.q_show_results.format(**context)
			results = connection.execute(text(show_results_query))

			st.dataframe(results)

	else:
		st.write('Please select a race and timing software. You need to choose a race and timing software before you can upload results.')

	connection.close()
engine.dispose()