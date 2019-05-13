'''
Example script to send email.

@author: cinquini
'''

from email.mime.text import MIMEText
import smtplib
from threading import Thread

# CHANGEME
TO_ADDRESS = 'luca.cinquini@jpl.nasa.gov'
SUBJECT = "TEST MESSAGE"
MESSAGE = "CIAO"

EMAIL_SERVER = 'smtp.jpl.nasa.gov'
EMAIL_PORT = None
EMAIL_SENDER = 'esgf-node@jpl.nasa.gov'
EMAIL_USERNAME = None
EMAIL_PASSWORD = None
EMAIL_SECURITY = 'STARTTLS'

class EmailThread(Thread):
    '''Class that sends an email in a separate thread.'''
    
    def __init__ (self, toAddress, subject, message, fromAddress=EMAIL_SENDER, mime_type='plain'):
        
        Thread.__init__(self)
        
        self.toAddress = toAddress
        self.subject = subject
        self.message = message
        self.fromAddress = fromAddress
        self.mime_type=mime_type
        
    def run(self):
        
        #print "From: %s" % self.fromAddress
        # print "To: %s" % self.toAddress
        # print 'From: %s' % self.fromAddress 
        # print "Subject: %s" % self.subject
        # print "Message: %s" % self.message
        # print "Mime Type: %s" % self.mime_type
        
        # use local mail server
        #toUser.email_user(subject, message, from_email=fromAddress)
            
        # use email relay server
        msg = MIMEText(self.message, self.mime_type)
        msg['Subject'] = self.subject
        msg['From'] = self.fromAddress
        msg['To'] = self.toAddress    
        if EMAIL_PORT is not None:
            s = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)
        else:
            s = smtplib.SMTP(EMAIL_SERVER)
        s.starttls()
        if EMAIL_USERNAME and EMAIL_PASSWORD:
            s.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        s.sendmail(self.fromAddress, [self.toAddress], msg.as_string())
        s.quit()
        # print 'Email sent.'


if __name__ == '__main__':
    
    emailThread = EmailThread(TO_ADDRESS, SUBJECT, MESSAGE, fromAddress=EMAIL_SENDER)
    emailThread.start()