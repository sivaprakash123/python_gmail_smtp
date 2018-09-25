# Python code to send email with multiple attachments from your Gmail account 

import smtplib, os, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date

today = date.today()
#Add your Gmail sender Email address 
fromaddr = "testuser@gmail.com"
# Add comma separated To addresses to send email
toaddr = "sivaprakash123@gmail.com","email2@yahoo.com","email3@gmail.com"
# instance of MIMEMultipart
msg = MIMEMultipart()
 
# storing the senders email address  
msg['From'] = "testuser@gmail.com"
 
# storing the receivers email address 
msg['To'] = ",".join(toaddr)
# storing the subject 
msg['Subject'] = "My Reports"

# string to store the body of the mail
body = "Hi, \nAttached the reports \nThanks, \nSivaprakash R"
 
# attach the body with the msg instance
msg.attach(MIMEText(body, 'plain'))
 
# Add your file location which needs to be attached
attachments = ["/opt/report1-%s.csv"% (today), "/opt/report2-%s.csv"%(today)]

if 'attachments' in globals() and len('attachments') > 0: # are there attachments?
    for filename in attachments:
        f = filename
# instance of MIMEBase and named as p
        p = MIMEBase('application', "octet-stream")
# To change the payload into encoded form
        p.set_payload( open(f,"rb").read() )
# encode into base64
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
# attach the instance 'p' to instance 'msg'
        msg.attach(p)
 
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
 
# start TLS for security
s.starttls()
 
# Authentication
s.login(fromaddr, "Ku4Ood8ir8pa3ich")
 
# Converts the Multipart msg into a string
text = msg.as_string()
 
# sending the mail
s.sendmail(fromaddr, toaddr, text)
 
# terminating the session
s.quit()

