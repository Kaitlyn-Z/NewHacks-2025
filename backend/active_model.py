import pandas as pd
import sqlite3
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def load_latest_alerts():
    with sqlite3.connect("backend/alerts.db") as conn:
        df = pd.read_sql_query("""
            SELECT Ticker, Close, Volume, volume_z, Volume_Ratio, RSI
            FROM latest_alerts
        """, conn)
    return df

def compute_features(df: pd.DataFrame):
    X = df[['volume_z', 'Volume_Ratio', 'RSI', 'Close']].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled

# TRAINING OUR MODEL

def train_dummy_model(df: pd.DataFrame):
    y = (df['Volume_Ratio'] > 3).astype(int)  # extreme volume spike indicates YES
    X = compute_features(df)
    model = LogisticRegression()
    model.fit(X,y)
    return model

# Predicting Confidence with Logistic Regression:

def predict_confidence(df: pd.DataFrame):
    model = train_dummy_model(df)
    X = compute_features(df)
    probs = model.predict_proba(X)[:,1]  # probability of class 1 (alert)
    df['Confidence'] = probs
    return df[['Ticker', 'Confidence']]
