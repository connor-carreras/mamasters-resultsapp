import streamlit as st
import pandas as pd

import calendar
import time
import urllib.parse
from sqlalchemy import text
from sqlalchemy import create_engine
from tabulate import tabulate
from datetime import datetime
import os
import season_queries


st.title("Iron Man Results")

firebolt_id = os.getenv('FIREBOLT_ID')
firebolt_secret = os.getenv('FIREBOLT_SECRET')

secret = urllib.parse.quote_plus(firebolt_secret)
engine = create_engine("firebolt://" + firebolt_id + ":" + secret + "@mamasters/ingest_engine?account_name=mamasters")

with st.expander("ℹ️ Understand the Iron Man award"):
	st.markdown("""
		**What is the Iron Man award?**
		- Fred and Beth Forbes created the Iron Man award to honor Bill Surette who had finished every race the year before. 
		The Iron Man award is about dedication. 
		It is about commitment. 
		It’s about dragging your ass to the hill. 
		It’s about taking the vacation time and getting yelled at by your spouse. 
		It’s about kicking out from the start and, quite frankly, it’s about finishing. 
		Have the balls to start and the smarts to finish. 
		It’s the grit award. The Gnarly Charlie award. 
		It’s the "you may not be fast but you get a cool trophy" award. 
		It’s about the heart.

		**Iron Man award rules**
		- The Iron Man is awarded to the person, male or female, with the most race finishes from the current season. An individual can only win the Iron Man once.
		- Tiebreak 1: If more than one person has the same number of race finishes, the Iron Man is awarded to the person with the most individual run finishes.
		- Tiebreak 2: If more than one person has the same number of run finishes, the Iron Man is awarded to the person with the most race finishes from the previous season.
		- Tiebreak 3: If more than one person has the same number of race finishes from the previous season, the Iron Man is awarded to the person with the most events entered over the previous two seasons.

		**Previous Iron Man winners**
		- 2006  Bill Surret
		- 2007  Beth Forbes
		- 2008  Bill Surret
		- 2009  Mel Foy
		- 2010  Ed Bassett
		- 2011  Michael J. Misencik
		- 2012  Wolfgang F. Bauer
		- 2013  Fred Forbes
		- 2014  Steve Zilli
		- 2015  William J. Pammer
		- 2016  James Neel
		- 2017  Kathy Hart
		- 2018  Greg Gallup
		- 2019  Carol Tomassetti
		- 2020  Jim Tomassetti
		- 2021  Karen Sanderson
		- 2022  Russell Kincaid
		- 2023  Deb Adams
		- 2024  Jesse Stevenson
	""")

with engine.connect() as connection:

	selected_season = st.selectbox('Season', ("2024-2025"), index=None, placeholder="Choose a season...")

	if selected_season == None:
		st.write('No season selected.')