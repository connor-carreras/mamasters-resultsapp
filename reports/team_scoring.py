import streamlit as st
import pandas as pd

import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine
from tabulate import tabulate
import os
import team_queries

st.set_page_config(page_title="Mid-Atlantic Masters: Race Results (Team)")

st.title("Team Results")

engine = create_engine("duckdb:///md:mamasters")

with st.expander("ℹ️ Understand team scoring"):
	st.markdown("""
		**Joining a Team**
		- Mid-Atlantic teams can have up to 15 members.
		- All members of a team must have paid Mid-Atlantic membership dues for the current season.
		- If you would like to join a team, please reach out to racing@mamasters.org, or contact a current team captain.

		**Calculating Team Scores**
		1. The race times for all team members are adjusted based on a time handicapping system. Our handicaps take both age and gender into account.
		2. We calculate a "Ghost Time" based on the handicapped time of the slowest racer that qualified for team scoring, plus 30 seconds. 
		3. For each team, the four fastest handicapped times count towards the total team time. If there are not four racers from a given team participating, one or more Ghost Times will be counted.
		4. Teams are ranked based on the total time for the top four racers on each team.
		5. Teams earn World Cup points based on their finish position.
	""")

with engine.connect() as connection:
	col1, col2 = st.columns(2)

	with col1:
		selected_season = st.selectbox('Season', ("2025-2026","2024-2025"), index=None, placeholder="Choose a season...")

	with col2:
		options = connection.execute(text(f"""
			select distinct(racekey) from results_vw where season = '{selected_season}' order by 1;
			"""))
		selected_option = st.selectbox('Race', options, index=None, placeholder="Choose a race...")

		team_exists = connection.execute(text(f"""
			select count(*) as num_records from team_results
			where racekey = '{selected_option}'
			"""))
		teamcount = team_exists.fetchone()
		teamcountstring = teamcount._mapping["num_records"]

	if selected_option == None:
		st.write('No race selected.')

	else:
		context = {**globals(), **locals()}
		get_teams_list = team_queries.q_teams_list.format(**context)
		teams = connection.execute(text(get_teams_list))

###Generate Visuals
		for row in teams:
			with st.container():
				team = row.team
				rank = row.team_rank
				total = row.team_total
				points = row.points

				col1, col2, col3 = st.columns(3)
				with col1:
					st.markdown(f"##### Rank {rank}: {team}")
				with col2:
					st.markdown(f"##### Total Time: {total}")
				with col3:
					st.markdown(f"##### {points} Points")
				with engine.connect() as conn_inner:
					context = {**globals(), **locals()}
					get_team_results = team_queries.q_team_results.format(**context)
					results = conn_inner.execute(text(get_team_results))
					st.dataframe(results, hide_index=True)
					conn_inner.close()
				engine.dispose()

	connection.close()

engine.dispose()
