# FastAPI backend

from fastapi import FastAPI, Request
from pydantic import BaseModel
import sqlite3
from backend.notifier import send_alert_email

app = FastAPI()

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

# Auto-generates a databse (file in directory is alerts.db) to store user preferences for email alerts.

@app.post("/register") # This function will handle HTTP POST requests sent to the /register URL path
async def register_user(pref: UserPreference): # Tells FastAPI what to do when a POST request is recieved
    # UserPreference parses the incoming JSON body from React frontend into an object in Python (defined earlier)
    alerts_str = ",".join(pref.alerts) # joins list into single string so it can be stored more easily
    with sqlite3.connect("backend/alerts.db") as conn: # connects to SQLite database file, alerts.db (in this directory)
        conn.execute("REPLACE INTO user_prefs (email, alerts) VALUES (?, ?)", (pref.email, alerts_str)) # Inserts or updates user preference
        # (Stores email + selected alert levels)
    return {"status": "ok", "message": f"Preferences saved for {pref.email}"} # Confirms to frontend that user preferences are saved

