import streamlit as st
import pandas as pd

import urllib.parse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from tabulate import tabulate
import racer_queries
import os

st.markdown("""
<style>
div[data-testid="stMetric"] > div[data-testid="stMetricValue"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
}

div[data-testid="stMetricValue"] {
    font-size: 20px !important;
}
</style>
"""
, unsafe_allow_html=True)

st.set_page_config(page_title="Mid-Atlantic Masters: Racer Lookup")


st.title("Racer Lookup")

engine = create_engine("duckdb:///md:mamasters")

with engine.connect() as connection:

	col1, col2 = st.columns(2)

	with col1:
		selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), index=None, placeholder="Choose a season...")

	with col2:
		options = connection.execute(text(f"""
		select distinct(name) from results_by_gender_vw where season = '{selected_season}' order by 1;
		"""))
		name = st.selectbox('Racer Name', options, index=None, placeholder="Choose a racer...")

	if name == None:
		st.write('No racer selected.')

	else:
		context = {**globals(), **locals()}
		get_best_discipline = racer_queries.q_best_discipline.format(**context)
		discipline_output = connection.execute(text(get_best_discipline))
		discipline_row = discipline_output.fetchone()
		best_discipline=discipline_row._mapping["best_discipline"]

		get_best_result = racer_queries.q_best_result.format(**context)
		best_result_output = connection.execute(text(get_best_result))
		result_row = best_result_output.fetchone()
		best_race = result_row._mapping["racekey"]
		best_race_description = result_row._mapping["description"]


		a, b = st.columns(2)
		with a:
			st.markdown(f"#### Result Summary")
			st.metric(label="Best Result", value=best_race, delta=best_race_description, border=True, height="stretch", delta_arrow="off")
			st.metric(label="Best Discipline", value=best_discipline, border=True, height="stretch")

		with b:
			st.markdown(f"#### Similar Racers")
			st.markdown(f"Shows the 5 racers who are most similar to you based on average race points and overall finish position.")
			get_similar_racers = racer_queries.q_similar_racers.format(**context)
			racers = connection.execute(text(get_similar_racers))
			st.table(racers, border="horizontal")

		st.markdown(f"#### Race Results: {selected_season} Season")
		tab1, tab2, tab3, tab4 = st.tabs(["All Results","Slalom Results", "Giant Slalom Results", "Super-G Results"])

		with tab1:
			get_racer_results = racer_queries.q_racer_results.format(**context)
			results = connection.execute(text(get_racer_results))

			st.dataframe(results,
				column_config={
					"link": st.column_config.LinkColumn(
						"Link to Results",
						display_text="View Results"
						)
					},
				hide_index=True)


		with tab2:
			discipline="Slalom"
			context = {**globals(), **locals()}
			get_racer_results = racer_queries.q_by_discipline.format(**context)
			results = connection.execute(text(get_racer_results))

			st.dataframe(results,
				column_config={
					"link": st.column_config.LinkColumn(
						"Link to Results",
						display_text="View Results"
						)
					},
				hide_index=True)

		with tab3:
			discipline="Giant Slalom"
			context = {**globals(), **locals()}
			get_racer_results = racer_queries.q_by_discipline.format(**context)
			results = connection.execute(text(get_racer_results))

			st.dataframe(results,
				column_config={
					"link": st.column_config.LinkColumn(
						"Link to Results",
						display_text="View Results"
						)
					},
				hide_index=True)

		with tab4:
			discipline="Super-G"
			context = {**globals(), **locals()}
			get_racer_results = racer_queries.q_by_discipline.format(**context)
			results = connection.execute(text(get_racer_results))

			st.dataframe(results,
				column_config={
					"link": st.column_config.LinkColumn(
						"Link to Results",
						display_text="View Results"
						)
					},
				hide_index=True)

	connection.close()

engine.dispose()
