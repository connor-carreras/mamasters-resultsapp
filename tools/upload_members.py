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
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
import os
import ingestion_queries

st.title("Upload Members Data")

st.markdown("Use this page to upload the members CSV file from Admin Ski Racing.")

aws_key = os.getenv("AWS_KEY")
aws_secret =os.getenv("AWS_SECRET")

racing_md_token =os.getenv("RACING_MD_TOKEN")

engine = create_engine("duckdb:///md:mamasters?motherduck_token={racing_md_token}")

with engine.connect() as connection:

	selected_season = st.selectbox('Season', ("2025-2026","2024-2025","2023-2024"), index=None, placeholder="Choose a season...")


	if selected_season == None:
		st.write('Please select a season. You need to choose a season before you can update the members file.')

	else:
		uploaded_file = st.file_uploader("Upload the members CSV from Admin Ski Racing.", type=["csv"])

		if uploaded_file is not None:
			name = "mam_members.csv"
			csv = uploaded_file.read()

			s3 = boto3.client(
			service_name="s3",
			region_name="us-east-1",
			aws_access_key_id=aws_key,
			aws_secret_access_key=aws_secret,
			)

			bucket_name = "mamasters-results"
			s3.put_object(
			Body=csv,
			Bucket=bucket_name,
			Key=name
			)
			st.write("File successfully uploaded!")


			context = {**globals(), **locals()}
			copy_members_query = ingestion_queries.q_copy_members.format(**context)
			connection.execute(text(copy_members_query))
			connection.commit()

			st.write("Members table has been refreshed!")

			st.markdown("#### Preview of latest members data:")
			context = {**globals(), **locals()}
			show_members_query = ingestion_queries.q_show_members.format(**context)
			results = connection.execute(text(show_members_query))

			st.dataframe(results)

	connection.close()
engine.dispose()