import streamlit.components.v1 as components
import httpx
import os

connor_md_prod_token = os.getenv("CONNOR_MD_PROD_TOKEN")
connor_md_prod_user =os.getenv("CONNOR_MD_PROD_USER")

DIVE_ID = os.getenv("DIVE_ID")

response = httpx.post(
    f"https://api.motherduck.com/v1/dives/{DIVE_ID}/embed-session",
    headers={
        "Authorization": f"Bearer {connor_md_prod_token}",
        "Content-Type": "application/json",
    },
    json={"username": f"{connor_md_prod_user}"},
)
response.raise_for_status()
session = response.json()["session"]
# Return this session string to your frontend

components.iframe(f"https://embed-motherduck.com/sandbox/#session={session}", height=800, scrolling=True)
