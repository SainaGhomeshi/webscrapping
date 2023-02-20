import smtplib
from email.mime.text import MIMEText


def send_email(body, recipients):
    msg = MIMEText(body)
    sender = 'web.scraping.asic@gmail.com'
    password = '!@#123qwe'
    msg['Subject'] = 'Liquidation notification'
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()
