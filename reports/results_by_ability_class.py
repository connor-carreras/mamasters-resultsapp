import streamlit as st
import pandas as pd

import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine

from tabulate import tabulate
import finals_ability_classes
import os

st.set_page_config(page_title="Mid-Atlantic Masters: Finals Ability Class Results")


st.title("Finals Ability Class Results")

engine = create_engine("duckdb:///md:mamasters")

with st.expander("ℹ️ Understand finals ability class scoring"):
	st.markdown("""
		**Ability Class Scoring**

		Groups are designed to give everyone a chance for a medal who may not typically have a good shot in their respective age class. 
		Groups are created based on each racer's overall season performance and known ability.
	""")

with engine.connect() as connection:

	selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), index=None, placeholder="Choose a season...")


	context = {**globals(), **locals()}
	get_classes_query = finals_ability_classes.q_class_list.format(**context)
	classes = connection.execute(text(get_classes_query))

	for row in classes:
		with st.container():
			gender = row.gender
			gender_header=row.gender_header
			ability_class = row.ability_class


			st.markdown(f"##### {gender_header} {ability_class} Results")
			with engine.connect() as conn_inner:
				context = {**globals(), **locals()}
				get_results_query = finals_ability_classes.q_ability_scores.format(**context)
				results = conn_inner.execute(text(get_results_query))

				st.dataframe(results)
				conn_inner.close()
			engine.dispose()

	connection.close()

engine.dispose()
