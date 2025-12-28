import streamlit as st
import pandas as pd
import setuptools

import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine

from tabulate import tabulate
from fpdf import FPDF
import gender_queries
import class_queries
import team_queries
import season_queries
import os
from datetime import datetime

@st.cache_data
def results_by_gender_pdf(selected_option):
	context = {**globals(), **locals()}
	gender_results_exist = gender_queries.q_gender_results_exist.format(**context)
	results_exist = connection.execute(text(gender_results_exist))
	resultscount = results_exist.fetchone()
	resultscountstring = resultscount._mapping["num_records"]

	if resultscountstring <= 0:
		context = {**globals(), **locals()}
		genders_insert_query = gender_queries.q_insert_results_by_gender.format(**context)
		connection.execute(text(genders_insert_query))

	else:
		pass

	context = {**globals(), **locals()}
	get_genders_query = gender_queries.q_get_genders.format(**context)
	genders = connection.execute(text(get_genders_query))

	with open("gender_results.txt", "w") as genders_file:
		genders_file.write(f"{selected_option}: Results by Gender\n\n")
		for row in genders:
			with st.container():

				gender = row.gender
				gender_header=row.gender_header

				genders_file.write(f"{gender_header} - Overall Individual Results\n")

				context = {**globals(), **locals()}
				get_results_query = gender_queries.q_select_results_by_gender.format(**context)
				gender_results = connection.execute(text(get_results_query))

				table = [r._asdict() for r in gender_results]
				items = []
				header = ['Place','Name','Class','Gender','Run 1','Run 2','Combined','WC Points','Race Points']
				for row in table:
					items.append(list(row.values()))
				genders_file.write(tabulate(items, headers=header))
				genders_file.write("\n\n")

	gender_pdf = FPDF()
	gender_pdf.add_page()
	gender_pdf.add_font('Consolas', '', './static/CONSOLA.TTF', uni=True)
	gender_pdf.set_font("Consolas", size=8)

	gender_file2 = open("gender_results.txt", 'r+')

	for x in gender_file2: 
		gender_pdf.cell(40,5, txt = x, ln = 1, align = 'L')

	gender_output_pdf=bytes(gender_pdf.output(dest='S'))
	return gender_output_pdf


@st.cache_data
def results_by_class_pdf(selected_option):
	context = {**globals(), **locals()}
	class_results_exist = class_queries.q_class_results_exist.format(**context)
	results_exist = connection.execute(text(class_results_exist))
	resultscount = results_exist.fetchone()
	resultscountstring = resultscount._mapping["num_records"]

	if resultscountstring <= 0:
		context = {**globals(), **locals()}
		classes_insert_query = class_queries.q_class_insert.format(**context)
		connection.execute(text(classes_insert_query))

	else:
		pass

	context = {**globals(), **locals()}
	get_classes_query = class_queries.q_class_list.format(**context)
	classes = connection.execute(text(get_classes_query))

	with open("class_results.txt", "w") as classes_file:
		classes_file.write(f"{selected_option}: Results by Age Class\n\n")

		context = {**globals(), **locals()}
		medals_count_query = class_queries.q_medals_list.format(**context)
		medals_count = connection.execute(text(medals_count_query))
		medalscount = medals_count.fetchone()
		total_medals = medalscount._mapping["total_medals"]
		total_gold = medalscount._mapping["total_gold"]
		total_silver = medalscount._mapping["total_silver"]
		total_bronze = medalscount._mapping["total_bronze"]

		classes_file.write(f"{total_medals} Medals Needed: {total_gold} Gold, {total_silver} Silver, {total_bronze} Bronze\n\n")

		for row in classes:
			with st.container():
				gender = row.gender
				gender_header=row.gender_header
				raceclass = row.raceclass

				classes_file.write(f"{gender_header} Class {raceclass} Results\n")

				context = {**globals(), **locals()}
				get_class_results = class_queries.q_class_results.format(**context)
				classes_results = connection.execute(text(get_class_results))

				table = [r._asdict() for r in classes_results]
				items = []
				header = ['Place','Name','Class','Gender','Run 1','Run 2','Combined','WC Points','Race Points']
				for row in table:
					items.append(list(row.values()))
				classes_file.write(tabulate(items, headers=header))
				classes_file.write("\n\n")


	classes_pdf = FPDF()
	classes_pdf.add_page()
	classes_pdf.add_font('Consolas', '', './static/CONSOLA.TTF', uni=True)
	classes_pdf.set_font("Consolas", size=8)

	classes_file2 = open("class_results.txt", 'r+')

	for x in classes_file2: 
		classes_pdf.cell(40,5, txt = x, ln = 1, align = 'L')

	classes_output_pdf=classes_pdf.output()
	return classes_output_pdf


@st.cache_data
def results_by_team_pdf(selected_option):
	context = {**globals(), **locals()}
	team_results_exist = team_queries.q_team_results_exist.format(**context)
	results_exist = connection.execute(text(team_results_exist))
	resultscount = results_exist.fetchone()
	resultscountstring = resultscount._mapping["num_records"]

	if resultscountstring <= 0:
		context = {**globals(), **locals()}
		teams_insert_query = team_queries.q_insert_teams.format(**context)
		connection.execute(text(teams_insert_query))

	else:
		pass

	context = {**globals(), **locals()}
	get_teams_list = team_queries.q_teams_list.format(**context)
	teams = connection.execute(text(get_teams_list))

	with open("teams_results.txt", "w") as teams_file:
		teams_file.write(f"{selected_option}: Team Results\n\n")
		for row in teams:
			with st.container():
				team = row.team
				rank = row.team_rank
				total = row.team_total
				points = row.points

				teams_file.write(f"Rank {rank}: {team}, Total Time: {total}, {points} Points\n")

				context = {**globals(), **locals()}
				get_team_results = team_queries.q_team_results.format(**context)
				teams_results = connection.execute(text(get_team_results))

				table = [r._asdict() for r in teams_results]
				items = []
				header = ['Name','Class','Gender','Run 1','Run 2','Total','Rank','Count Score']
				for row in table:
					items.append(list(row.values()))
				teams_file.write(tabulate(items, headers=header))
				teams_file.write("\n\n")

	teams_pdf = FPDF()
	teams_pdf.add_page()
	teams_pdf.add_font('Consolas', '', './static/CONSOLA.TTF', uni=True)
	teams_pdf.set_font("Consolas", size=10)

	teams_file2 = open("teams_results.txt", 'r+')

	for x in teams_file2: 
		teams_pdf.cell(40,5, txt = x, ln = 1, align = 'L')

	teams_output_pdf=teams_pdf.output()
	return teams_output_pdf


@st.cache_data
def season_results_by_gender(selected_option):
	context = {**globals(), **locals()}
	get_season_gender_query = season_queries.q_list_genders.format(**context)
	season_genders = connection.execute(text(get_season_gender_query))

	with open("season_gender_results.txt", "w") as season_genders_file:
		season_genders_file.write(f"Mid-Atlantic Masters Season Standings by Gender (All Racers)\n\n")

		season_genders_file.write(f"Standings as of {report_date}\n")
		season_genders_file.write(f"Minimum 6 races required to qualify for season scoring.\n")
		season_genders_file.write(f"2024-2025 season has 24 races total. Best 12 finishes count.\n\n")


		for row in season_genders:
			gender = row.gender
			gender_header=row.gender_header

			season_genders_file.write(f"{gender_header} - Overall Season Standings\n")

			context = {**globals(), **locals()}
			get_season_genders_results = season_queries.q_2025_new_by_gender.format(**context)
			season_genders_results = connection.execute(text(get_season_genders_results))

			table = [r._asdict() for r in season_genders_results]
			items = []
			header = ['Place','Name','Points','St','Fn','Score 1','Score 2','Score 3','Score 4','Score 5','Score 6','Score 7','Score 8','Score 9','Score 10','Score 11','Score 12','Discarded Scores']
			for row in table:
				items.append(list(row.values()))
			season_genders_file.write(tabulate(items, headers=header))
			season_genders_file.write("\n\n")

	season_genders_pdf = FPDF(orientation="landscape")
	season_genders_pdf.add_page()
	season_genders_pdf.add_font('Consola', '', './static/CONSOLA.TTF', uni=True)
	season_genders_pdf.set_font("Consola", size=6)

	season_genders_file2 = open("season_gender_results.txt", 'r+')

	for x in season_genders_file2: 
		season_genders_pdf.cell(10,4, txt = x, ln = 1, align = 'L')

	season_genders_output_pdf=season_genders_pdf.output()
	return season_genders_output_pdf

@st.cache_data
def season_results_by_class(selected_option):
	context = {**globals(), **locals()}
	get_season_class_query = season_queries.q_class_list.format(**context)
	season_classes = connection.execute(text(get_season_class_query))

	with open("season_gender_results.txt", "w") as season_classes_file:
		season_classes_file.write(f"Mid-Atlantic Masters Season Standings by Age Class (All Racers)\n\n")

		season_classes_file.write(f"Standings as of {report_date}\n")
		season_classes_file.write(f"Minimum 6 races required to qualify for season scoring.\n")
		season_classes_file.write(f"2024-2025 season has 24 races total. Best 12 finishes count.\n\n")


		for row in season_classes:
			gender = row.gender
			gender_header=row.gender_header
			raceclass = row.raceclass

			season_classes_file.write(f"{gender_header} Class {raceclass} - Overall Season Standings\n")

			context = {**globals(), **locals()}
			get_season_classes_results_query = season_queries.q_2025_new_by_class.format(**context)
			season_classes_results = connection.execute(text(get_season_classes_results_query))

			table = [r._asdict() for r in season_classes_results]
			items = []
			header = ['Place','Name','Points','St','Fn','Score 1','Score 2','Score 3','Score 4','Score 5','Score 6','Score 7','Score 8','Score 9','Score 10','Score 11','Score 12','Discarded Scores']
			for row in table:
				items.append(list(row.values()))
			season_classes_file.write(tabulate(items, headers=header))
			season_classes_file.write("\n\n")

	season_classes_pdf = FPDF(orientation="landscape")
	season_classes_pdf.add_page()
	season_classes_pdf.add_font('Consola', '', './static/CONSOLA.TTF', uni=True)
	season_classes_pdf.set_font("Consola", size=6)

	season_classes_file2 = open("season_gender_results.txt", 'r+')

	for x in season_classes_file2: 
		season_classes_pdf.cell(10,4, txt = x, ln = 1, align = 'L')

	season_classes_output_pdf=season_classes_pdf.output()
	return season_classes_output_pdf

def clear_cache():
	results_by_gender_pdf.clear()
	results_by_class_pdf.clear()
	results_by_team_pdf.clear()
	season_results_by_gender.clear()
	season_results_by_class.clear()

st.title("Generate Result PDFs")

firebolt_id = os.getenv('FIREBOLT_ID')
firebolt_secret = os.getenv('FIREBOLT_SECRET')

secret = urllib.parse.quote_plus(firebolt_secret)
engine = create_engine("firebolt://" + firebolt_id + ":" + secret + "@mamasters/ingest_engine?account_name=mamasters")

report_date = datetime.today().strftime('%Y-%m-%d')

with engine.connect() as connection:
	col1, col2 = st.columns(2)

	with col1:
		selected_season = st.selectbox('Season', ("2025-2026","2024-2025","2023-2024"), index=None, placeholder="Choose a season...")

	with col2:
		options = connection.execute(text(f"""
			select distinct(racekey) from results_vw where season = '{selected_season}' order by 1;
			"""))
		selected_option = st.selectbox('Race', options, index=None, placeholder="Choose a race...")

	if selected_option == None:
		st.write('No race selected.')

	else:
		st.button('Re-generate PDFs', on_click=clear_cache)
		race_results, season_standings = st.columns(2)

		with race_results:
			st.markdown(f"#### Race Results")

			##Generate Results by Gender PDF
			st.download_button(
				label="Download Results by Gender",
				data=results_by_gender_pdf(selected_option),
				file_name="gender_results.pdf",
				mime="application/pdf",
			)

			##Generate Results by Class PDF
			st.download_button(
				label="Download Results by Class",
				data=bytes(results_by_class_pdf(selected_option)),
				file_name="class_results.pdf",
				mime="application/pdf",
			)

			##Generate results by team PDF
			st.download_button(
				label="Download Results by Team",
				data=bytes(results_by_team_pdf(selected_option)),
				file_name="teams_results.pdf",
				mime="application/pdf",
			)

		with season_standings:
			st.markdown(f"#### Season Standings")
			
			##Generate Season Standings by Gender PDF
			st.download_button(
				label="Download Season Standings by Gender",
				data=bytes(season_results_by_gender(selected_option)),
				file_name="season_results_by_gender.pdf",
				mime="application/pdf",
			)

			##Generate Season Standings by Class PDF
			st.download_button(
				label="Download Season Standings by Class",
				data=bytes(season_results_by_class(selected_option)),
				file_name="season_results_by_class.pdf",
				mime="application/pdf",
			)
		connection.close()
engine.dispose()
