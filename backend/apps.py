# FastAPI backend

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware # to allow requests from React frontend
from pydantic import BaseModel
import sqlite3
# from backend.notifier import send_alert_email: Is this needed?
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server 
    # --> need to to communicate with FastAPI backend (hosted on localhost:8000)
    allow_methods=["*"],
    allow_headers=["*"]
)

class UserPreference(BaseModel): # When a class inherits from pydantic.BaseModel, 
    # it gains the ability to automatically validate incoming data based on the type 
    # annotations provided for its attributes.
    email: str
    alerts: list[str]

def init_db():
    with sqlite3.connect("backend/alerts.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_prefs (
                email TEXT PRIMARY KEY,
                alerts TEXT
            )
        """)
init_db()

# Auto-generates a database (file in directory is alerts.db) to store user preferences for email alerts.

@app.post("/preferences") # (Dropdown menu? Or separate url path?) 
async def save_preferences(pref: UserPreference): # Tells FastAPI what to do when a POST request is recieved
    # UserPreference parses the incoming JSON body from React frontend into an object in Python (defined earlier)
    alerts_str = ",".join(pref.alerts) # joins list into single string so it can be stored more easily
    with sqlite3.connect("backend/alerts.db") as conn: # connects to SQLite database file, alerts.db (in this directory)
        conn.execute("REPLACE INTO user_prefs (email, alerts) VALUES (?, ?)", (pref.email, alerts_str)) # Inserts or updates user preference
        # (Stores email + selected alert levels)
    return {"status": "ok", "message": f"Preferences saved for {pref.email}"} # Confirms to frontend that user preferences are saved

@app.get("/preferences/{email}") # GET request to retrieve user preferences based on email
async def get_preferences(email: str):
    with sqlite3.connect("backend/alerts.db") as conn:
        row = conn.execute("SELECT alerts FROM user_prefs WHERE email=?", (email,)).fetchone()
    if row:
        return {"email": email, "alerts": row[0].split(",")}
    else:
        return {"email": email, "alerts": []}
    
@app.get("/latest-alerts") # Uses latest_alerts table in alerts.db
async def latest_alerts():
    conn = sqlite3.connect("backend/alerts.db")
    rows = conn.execute("SELECT Ticker, Close, Volume, volume_z, Volume_Ratio, Volume_Alert, RSI, Timestamp FROM latest_alerts").fetchall()
    conn.close()
    return [{"Ticker": r[0], "Close": r[1], "Volume": r[2], "volume_z": r[3], "Volume_Ratio": r[4], "Volume_Alert": r[5], "RSI": r[6], "Timestamp": r[7]} for r in rows]
