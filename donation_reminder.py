from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from flask_mail import Message, Mail
from models import Donor  
from app import db

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Define the reminder function
def send_monthly_reminders():
    # Query the database to find donors who need reminders
    donors = Donor.query.filter_by(needs_reminder=True).all()

    for donor in donors:
        # Send reminders to those donors
        msg = Message('Monthly Donation Reminder', sender='your_email@example.com', recipients=[donor.email])
        msg.body = 'Do not forget to make your monthly donation!'

        try:
            mail = Mail(current_app)
            mail.send(msg)
            # Update the donor's reminder status or log the successful reminder
            donor.needs_reminder = False
            db.session.commit()
        except Exception as e:
            # Handle email sending errors
            print(f"Error sending email to {donor.email}: {str(e)}")

scheduler.add_job(send_monthly_reminders, CronTrigger(day_of_month='1', hour='10'))  # Updated the 'day' argument and format
scheduler.start()
