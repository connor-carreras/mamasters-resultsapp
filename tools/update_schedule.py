import streamlit as st
import pandas as pd

import os
import urllib.parse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from streamlit import session_state as ss
from data_changes import process_cols, select_cols, insert_cols, delete_cols

st.title("Update Season Schedule")

st.markdown("Use this page to update the season schedule. You can add, remove, and change races as long as the date of your change is on or before the date of the race.")

engine = create_engine("duckdb:///md:mamasters")

##Put a dropdown in to choose the season
##Add a filter to the read sql table command to only display records from the selected season and only let you update records for future races
if "uploader_key" not in st.session_state:
	st.session_state.uploader_key = 0

def update_key():
	st.session_state.uploader_key += 1
	get_schedule.clear()

selected_season = st.selectbox('Season', ("2026-2027","2025-2026","2024-2025","2023-2024"), index=None, placeholder="Choose a season...", on_change=update_key)
tabname = "schedule_test"

@st.cache_data
def get_schedule():
	with engine.connect() as connection:
		sql= f"select * from schedule where season = '{selected_season}';"
		df= pd.read_sql(sql, engine)
		return df
		connection.close()
	engine.dispose()

if selected_season != None:
	st.write("Edit the data below. When you are done, click 'Submit Changes' to save your work.")
	schedule=get_schedule()
	ss.edited_rows = st.data_editor(schedule, num_rows="dynamic", key='ed')
	st.write(st.session_state["ed"])

	if st.button('Submit Changes'):
		for rec in ss.ed["edited_rows"]:
			idx = int(rec)
			updt = process_cols(ss.ed["edited_rows"][rec], tabname)
			where = select_cols(schedule, idx)
			update_stmt = updt + " " + where
			st.write(update_stmt)

		for irec in ss.ed["added_rows"]:
			insert_stmt = insert_cols(irec, tabname)
			st.write(insert_stmt)

		for rec in ss.ed["deleted_rows"]:
			idx = int(rec)
			delete_stmt = delete_cols(idx, schedule, tabname)
			st.write(delete_stmt)

		with engine.connect() as connection:
			if 'delete_stmt' in locals():
				connection.execute(text(delete_stmt))
			if 'update_stmt' in locals():
				connection.execute(text(update_stmt))
			if 'insert_stmt' in locals():
				connection.execute(text(insert_stmt))
			connection.commit()
			connection.close()
		engine.dispose()
		st.cache_data.clear()
		st.rerun()


