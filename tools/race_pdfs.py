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
import overall_queries
import os
from datetime import datetime

racing_md_token = os.getenv("RACING_MD_TOKEN")


@st.cache_data
def results_overall_pdf(selected_option):
	context = {**globals(), **locals()}
	overall_results_exist = overall_queries.q_overall_results_exist.format(**context)
	results_exist = connection.execute(text(overall_results_exist))
	resultscount = results_exist.fetchone()
	resultscountstring = resultscount._mapping["num_records"]

	if resultscountstring <= 0:
		context = {**globals(), **locals()}
		overall_insert_query = overall_queries.q_insert_overall_results.format(**context)
		connection.execute(text(overall_insert_query))
		connection.commit()

	else:
		pass

	with open("overall_results.txt", "w") as overall_file:
		overall_file.write(f"{selected_option}: Overall Results\n\n")
		with st.container():

			context = {**globals(), **locals()}
			get_overall_query = overall_queries.q_select_overall_results.format(**context)
			overall_results = connection.execute(text(get_overall_query))

			table = [r._asdict() for r in overall_results]
			items = []
			header = ['Place','Name','Class','Gender','Run 1','Run 2','Combined']
			for row in table:
				items.append(list(row.values()))
			overall_file.write(tabulate(items, headers=header))
			overall_file.write("\n\n")

	overall_pdf = FPDF()
	overall_pdf.add_page()
	overall_pdf.add_font('Consolas', '', './static/CONSOLA.TTF', uni=True)
	overall_pdf.set_font("Consolas", size=8)

	overall_file2 = open("overall_results.txt", 'r+')

	for x in overall_file2: 
		overall_pdf.cell(40,5, txt = x, ln = 1, align = 'L')

	overall_output_pdf=bytes(overall_pdf.output(dest='S'))
	return overall_output_pdf

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
		connection.commit()

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
				with engine.connect() as conn_inner:

					context = {**globals(), **locals()}
					get_results_query = gender_queries.q_select_results_by_gender.format(**context)
					gender_results = conn_inner.execute(text(get_results_query))

					table = [r._asdict() for r in gender_results]
					items = []
					header = ['Place','Name','Class','Gender','Run 1','Run 2','Combined','WC Points','Race Points']
					for row in table:
						items.append(list(row.values()))
					genders_file.write(tabulate(items, headers=header))
					genders_file.write("\n\n")
					conn_inner.close()
				engine.dispose()

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
		connection.commit()

	else:
		pass

	context = {**globals(), **locals()}
	get_classes_query = class_queries.q_class_list.format(**context)
	classes = connection.execute(text(get_classes_query))
	
	with engine.connect() as medals_conn:
		medals_count_query = class_queries.q_medals_list.format(**context)
		medals_count = medals_conn.execute(text(medals_count_query))
		medalscount = medals_count.fetchone()
		total_medals = medalscount._mapping["total_medals"]
		total_gold = medalscount._mapping["total_gold"]
		total_silver = medalscount._mapping["total_silver"]
		total_bronze = medalscount._mapping["total_bronze"]
		medals_conn.close()
	engine.dispose()

	with open("class_results.txt", "w") as classes_file:
		classes_file.write(f"{selected_option}: Results by Age Class\n\n")

		classes_file.write(f"{total_medals} Medals Needed: {total_gold} Gold, {total_silver} Silver, {total_bronze} Bronze\n\n")


		for row in classes:
			with st.container():
				gender = row.gender
				gender_header=row.gender_header
				raceclass = row.raceclass

				classes_file.write(f"{gender_header} Class {raceclass} Results\n")

				with engine.connect() as conn_inner2:
					context = {**globals(), **locals()}
					get_class_results = class_queries.q_class_results.format(**context)
					classes_results = conn_inner2.execute(text(get_class_results))

					table = [r._asdict() for r in classes_results]
					items = []
					header = ['Place','Name','Class','Gender','Run 1','Run 2','Combined','WC Points','Race Points']
					for row in table:
						items.append(list(row.values()))
					classes_file.write(tabulate(items, headers=header))
					classes_file.write("\n\n")
					conn_inner2.close()
				engine.dispose()


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
		connection.commit()

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

				with engine.connect() as conn_inner3:
					context = {**globals(), **locals()}
					get_team_results = team_queries.q_team_results.format(**context)
					teams_results = conn_inner3.execute(text(get_team_results))

					table = [r._asdict() for r in teams_results]
					items = []
					header = ['Name','Class','Gender','Run 1','Run 2','Total','Rank','Count Score']
					for row in table:
						items.append(list(row.values()))
					teams_file.write(tabulate(items, headers=header))
					teams_file.write("\n\n")
					conn_inner3.close()
				engine.dispose()

	teams_pdf = FPDF()
	teams_pdf.add_page()
	teams_pdf.add_font('Consolas', '', './static/CONSOLA.TTF', uni=True)
	teams_pdf.set_font("Consolas", size=10)

	teams_file2 = open("teams_results.txt", 'r+')

	for x in teams_file2: 
		teams_pdf.cell(40,5, txt = x, ln = 1, align = 'L')

	teams_output_pdf=teams_pdf.output()
	return teams_output_pdf

def clear_cache():
	results_by_gender_pdf.clear()
	results_by_class_pdf.clear()
	results_by_team_pdf.clear()
	results_overall_pdf.clear()

st.title("Generate Result PDFs")

racing_md_token =os.getenv("RACING_MD_TOKEN")

engine = create_engine(f"duckdb:///md:mamasters?motherduck_token={racing_md_token}")

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
		race_results, team_results = st.columns(2)

		with race_results:
			st.markdown(f"#### Race Results (Individual)")

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

			##Generate overall results PDF
			st.download_button(
				label="Download Overall Results",
				data=bytes(results_overall_pdf(selected_option)),
				file_name="overall_results.pdf",
				mime="application/pdf",
			)

		with team_results:
			st.markdown(f"#### Race Results (Team)")

			##Generate results by team PDF
			st.download_button(
				label="Download Results by Team",
				data=bytes(results_by_team_pdf(selected_option)),
				file_name="teams_results.pdf",
				mime="application/pdf",
			)

		connection.close()
engine.dispose()
