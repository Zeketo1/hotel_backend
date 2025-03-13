import smtplib

# Replace with your credentials
EMAIL = "ikorofrancis24@gmail.com"
PASSWORD = "pjzp zzyc dqth wikb"  # Gmail App Password (no spaces)

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    print("SMTP connection successful!")
except Exception as e:
    print(f"SMTP connection failed: {e}")
finally:
    if 'server' in locals():  # Ensure server exists before quitting
        server.quit()