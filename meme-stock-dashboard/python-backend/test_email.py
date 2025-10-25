#!/usr/bin/env python3
"""
Simple test script to verify Gmail SMTP credentials
"""
import smtplib

email = "liyunzi0902@gmail.com"
receiver = "liyunzi0902@gmail.com"
password = "pxhjmkgfjndgjhhb"  # 16 characters, no spaces

try:
    print(f"Testing Gmail SMTP connection...")
    print(f"Email: {email}")
    print(f"Password length: {len(password)} characters")
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print("TLS started successfully")
    
    server.login(email, password)
    print("✅ Login successful!")
    
    # Send test email
    subject = "Test from Meme Stock Dashboard"
    message = "This is a test email from your meme stock alerts system!"
    text = f"Subject: {subject}\n\n{message}"
    
    server.sendmail(email, receiver, text)
    print(f"✅ Test email sent to {receiver}")
    
    server.quit()
    print("✅ Connection closed successfully")
    print("\n🎉 All tests passed! Email service is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPlease check:")
    print("1. Gmail App Password is correct (16 characters, no spaces)")
    print("2. 2-Factor Authentication is enabled on your Gmail")
    print("3. App Password was generated correctly")
