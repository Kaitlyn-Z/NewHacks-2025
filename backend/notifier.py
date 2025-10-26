# Email sending logic 

# Created a GMAIL account just for this project (see Google Docs for Email and Password)

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

EMAIL_USER = "meme.watchlist25@gmail.com"
EMAIL_PASS = "dhxj mgug defo aonw"


###############

import smtplib #defines an SMTP client session object that can be used to 
# send mail to any internet machine with an SMTP or ESMTP listener daemon
from email.message import EmailMessage # class used to create and manipulate email messages  

def send_alert_email(to_email: str, ticker: str, alert: str, rsi: float, timestamp: str, price: float, volume: int, volume_ratio: float):
    msg = EmailMessage()
    msg["Subject"] = f"[Stock Alert] {ticker} - {alert}"
    msg["From"] = EMAIL_USER 
    msg["To"] = to_email

    body = ("A new stock has been added to your watchlist!\n\n"
        f"Stock: {ticker}\n"
        f"Alert Level: {alert}\n"
       # f"Mentions: {}\n".  # Are we gonna have the number of mentions from the web scraping?
        f"Volume: {volume}\n"
        f"Volume Ratio: {volume_ratio:.2f}\n"
        f"RSI: {rsi:.2f}\n\n"
        f"Timestamp: {timestamp}\n\n"
        f"Price: ${price:.2f}\n\n"
        "Check your dashboard for details."
    )
    msg.set_content(body)

    # Send via Gmail (requires an app password)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS) # CREATE AN EMAIL JUST FOR THIS PROJECT
        smtp.send_message(msg)

