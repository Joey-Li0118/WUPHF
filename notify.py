import smtplib
from dotenv import load_dotenv
import os
from email.mime.multipart import MIMEMultipart #MIME (Multipurpose Internet Mail Extensions)
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()

#create smtp session

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls() #start Transport Layer Security which encrypts smtp commands
sender_email_address = os.getenv("EMAIL_ADDRESS")
sender_email_password = os.getenv("EMAIL_PASSWORD")
s.login(sender_email_address, sender_email_password)
# message to be sent
receiver_email_address = "imageheart89@gmail.com"
message = MIMEMultipart()
message['Subject'] = "WUPHF"
message['From'] = sender_email_address
message['To'] = receiver_email_address
# sending the mail
body = "Body_of_the_mail"
  
# attach the body with the msg instance 
message.attach(MIMEText(body, 'plain')) 
  
# open the file to be sent  

# instance of MIMEBase and named as p 
 
s.send_message(message) #sendmail is different from send_message

# terminating the session
s.close()
