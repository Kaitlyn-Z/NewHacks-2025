# Email sending logic --> WORK IN PROGRESS

# Create a GMAIL account just for this project

import smtplib #defines an SMTP client session object that can be used to 
# send mail to any internet machine with an SMTP or ESMTP listener daemon
from email.message import EmailMessage # class used to create and manipulate email messages  

def send_alert_email(to_email: str, ticker: str, alert: str, volume_z: float, rsi: float):
    msg = EmailMessage()
    msg["Subject"] = f"[Stock Alert] {ticker} - {alert}"
    msg["From"] = "faris.abuain@gmail.com" # change this (i don't want my email showing up in public code)
    msg["To"] = to_email

    body = (
        f"Stock: {ticker}\n"
        f"Alert Level: {alert}\n"
       # f"Mentions: {}\n"
       # f" Volume: {volume}\n"
        f"RSI: {rsi:.2f}\n\n"
        "Check your dashboard for details."
    )
    msg.set_content(body)

    # Send via Gmail (requires an app password)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("faris.abuain@gmail.com", "YOUR_APP_PASSWORD") # CREATE AN EMAIL JUST FOR THIS PROJECT
        smtp.send_message(msg)
