import smtplib
import os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email(to_email, otp):

    try:
        subject = "Your OTP Code"
        message = f"Your OTP for password reset is: {otp}"

        email_text = f"Subject: {subject}\n\n{message}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to_email, email_text)
        server.quit()
        print("EMAIL USER:", EMAIL_USER)

        return True

    except Exception as e:
        print("Email sending failed:", e)
        return False
