import streamlit as st
import hmac
import os

if "role" not in st.session_state:
	st.session_state.role = None

ROLES = [None, "Admin"]

app_password = os.environ.get("APP_PASSWORD")

def login():
	st.header("Log in")

	with st.form("Credentials", clear_on_submit=True):
		password = st.text_input("Password", type="password")
		submitted = st.form_submit_button("Log in")
		if submitted:
			if password == app_password:
				st.session_state.role = 'Admin'
				st.rerun()
			else:
				st.error("Invalid password. Access denied.")
				st.stop()


role = st.session_state.role


login_page = st.Page(login, title="Log in", icon=":material/login:")

home_page = st.Page("tools/homepage.py", title="Instructions", icon=":material/info:", default=(role == "Admin"))
upload_page = st.Page("tools/upload_results.py", title="Upload race results", icon=":material/add_circle:")
members_page = st.Page("tools/upload_members.py", title="Update members file", icon=":material/group_add:")
# dsq_page = st.Page("tools/dsqs.py", title="Enter DSQs", icon=":material/delete:")
team_scoring = st.Page("reports/team_scoring.py", title="Team results", icon=":material/downhill_skiing:")
results_by_gender = st.Page("reports/results_by_gender.py", title="Results by gender", icon=":material/downhill_skiing:", default=(role == None))
results_by_class = st.Page("reports/results_by_class.py", title="Results by class", icon=":material/downhill_skiing:")
pa_cup_results = st.Page("reports/pa_cup.py", title="Pennsylvania Cup results", icon=":material/downhill_skiing:")
finals_ability_results = st.Page("reports/results_by_ability_class.py", title="Finals ability class results", icon=":material/downhill_skiing:")
season_by_team = st.Page("reports/season_by_team.py", title="Team season standings", icon=":material/downhill_skiing:")
season_by_gender = st.Page("reports/season_by_gender.py", title="Season standings by gender", icon=":material/downhill_skiing:")
season_by_class = st.Page("reports/season_by_class.py", title="Season standings by class", icon=":material/downhill_skiing:")
# iron_man = st.Page("reports/iron_man.py", title= "Iron Man standings", icon=":material/downhill_skiing:")
race_pdfs = st.Page("tools/race_pdfs.py", title="Generate result PDFs", icon=":material/description:")

data_tools = [home_page, upload_page, race_pdfs, members_page]
race_reports = [results_by_gender, results_by_class, team_scoring, pa_cup_results, finals_ability_results]
season_standings = [season_by_gender, season_by_class, season_by_team]
account_pages = [login_page]

st.set_page_config(page_title="Mid-Atlantic Masters Results App", page_icon=":material/downhill_skiing:", layout="wide")

st.logo("images/mam_logo_text_only.png", size="large")

page_dict = {}
if st.session_state.role in ["Admin"]:
	page_dict["Data Tools"] = data_tools
if st.session_state.role in [None, "Admin"]:
	page_dict["Race Reports"] = race_reports
if st.session_state.role in [None, "Admin"]:
	page_dict["Season Standings"] = season_standings
if st.session_state.role in [None, "Admin"]:
	page_dict["Account"] = account_pages

pg = st.navigation(page_dict)


pg.run()