import streamlit as st

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine

st.title("Mid-Atlantic Masters Results App")


st.subheader("Instructions")
st.markdown("""1. Click the "Upload race results" page. This is where you will upload the raw results provided to you by the mountain. The mountain will give you a file ending in ".NATFis". On your computer, edit the filename and change ".NATFis" to ".xml". Once you have an XML file, you can upload it to this tool.

2. Click the "Enter DSQs" page. Refer to the referee reports uploaded to WhatsApp. Select each of the racers who had a DSQ for the first run or the second run, and then click "Submit".  
	**IMPORTANT: You MUST enter DSQs before generating race result PDFs.**

3. Click the "Generate result PDFs" page. This page will produce the 5 PDF reports that you need to print for the awards ceremony. Note that the "Results by Class" PDF file will tell you the number of medals needed for the ceremony. 
	""")
