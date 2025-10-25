#!/usr/bin/env python3
"""
Simple script to run the Python email service
"""
import os
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting Python Email Service on port {port}")
    print(f"📧 SMTP Host: {os.getenv('SMTP_HOST', 'smtp.gmail.com')}")
    print(f"📧 Email Recipient: {os.getenv('EMAIL_RECIPIENT', 'Not configured')}")
    print(f"🌐 API Endpoint: http://localhost:{port}/api/email")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
