from flask import current_app
from flask_mail import Message
from flask_mail import Mail

def send_approval_email(charity):
    subject = "Your Charity Has Been Approved"
    recipients = [charity.email]  # Replace with the charity's email field
    sender = current_app.config['MAIL_USERNAME']  # Configure your sender email address

    message = "Congratulations! Your charity '{}' has been approved.".format(charity.name)

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = message

    mail = Mail(current_app)
    mail.send(msg)

def send_rejection_email(charity):
    subject = "Your Charity Has Been Rejected"
    recipients = [charity.email]  # Replace with the charity's email field
    sender = 'your_email@example.com'  # Configure your sender email address

    message = "We regret to inform you that your charity '{}' has been rejected.".format(charity.name)

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = message

    mail = Mail(current_app)
    mail.send(msg)  

def send_thank_you_email(charity):
    subject = "Thank You for Registering"
    recipients = [charity.email]  # Replace with the charity's email field
    sender = current_app.config['MAIL_USERNAME'] 

    message = 'Welcome to Tuinue Wasichana Charity Platform and Thank you for registering. Your registration is pending approval.'
    # Create a message object
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = message

    # Send the email
    mail = Mail(current_app)
    mail.send(msg)