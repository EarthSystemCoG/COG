from email.mime.text import MIMEText
import smtplib
from threading import Thread
from django.conf import settings
from cog.site_manager import siteManager

from cog.constants import SECTION_EMAIL

import logging

log = logging.getLogger(__name__)

class EmailConfig:
    '''
    Class that stores the email server connection properties from a local configuration file.
    Site specific values are read from the cog_settings.cfg file through the SiteManager class.
    '''
    
    def __init__(self):
        
        self.init = False
        
        if siteManager.hasConfig(SECTION_EMAIL):
            self.server = siteManager.get('EMAIL_SERVER', section=SECTION_EMAIL)
            if self.server is not None and self.server.strip() != '':
                self.port = siteManager.get('EMAIL_PORT', section=SECTION_EMAIL)
                self.sender = siteManager.get('EMAIL_SENDER', section=SECTION_EMAIL)
                self.username = siteManager.get('EMAIL_USERNAME', section=SECTION_EMAIL)
                self.password = siteManager.get('EMAIL_PASSWORD', section=SECTION_EMAIL)
                self.security = siteManager.get('EMAIL_SECURITY', section=SECTION_EMAIL)
                log.debug('Using email server=%s' %  self.server)
                log.debug('Using email port=%s' %  self.port)
                log.debug('Using email sender=%s' %  self.sender)
                log.debug('Using email username=%s' %  self.username)
                #log.debug('Using email password=%s' %  self.password)
                log.debug('Using email security=%s' %  self.security)
                self.init = True
            
        if not self.init:
            log.debug("Email configuration not found, email notification disabled")
            

# module scope email configuration
emailConfig = EmailConfig()

def notify(toUser, subject, message, mime_type='plain'):  # send 'plain' email by default
    '''Notifies a specific user by email.'''
    
    # send email in separate thread, do not wait   
    emailThread = EmailThread(toUser.email, subject, message, mime_type=mime_type)
    emailThread.start()


def sendEmail(toAddress, subject, message, fromAddress=None, mime_type='plain'):
    '''Sends email to a specific address.'''
    
    # send email in separate thread, do not wait
    emailThread = EmailThread(toAddress, subject, message, fromAddress, mime_type)
    emailThread.start()

        
class EmailThread(Thread):
    '''Class that sends an email in a separate thread.'''
    
    def __init__ (self, toAddress, subject, message, fromAddress=None, mime_type='plain'):
        Thread.__init__(self)
        self.toAddress = toAddress
        self.subject = subject
        self.message = message
        if fromAddress is not None:
            self.fromAddress = fromAddress
        elif emailConfig.init == True:
            self.fromAddress = emailConfig.sender
        else:
            self.fromAddress = None
        self.mime_type=mime_type
        
    def run(self):
        
        #print "From: %s" % self.fromAddress
        log.debug("To: %s" % self.toAddress)
        log.debug("Subject: %s" % self.subject)
        log.debug("Message: %s" % self.message)
        log.debug("Mime Type: %s" % self.mime_type)
        
        # use local mail server
        #toUser.email_user(subject, message, from_email=fromAddress)
        
        # use email relay server
        if emailConfig.init == True:
    
            # use email relay server
            msg = MIMEText(self.message, self.mime_type)
            msg['Subject'] = self.subject
            msg['From'] = self.fromAddress
            msg['To'] = self.toAddress    
            if emailConfig.port is not None:
                s = smtplib.SMTP(emailConfig.server, emailConfig.port)
            else:
                s = smtplib.SMTP(emailConfig.server)
            if emailConfig.security=='STARTTLS':
                s.starttls()
            if emailConfig.username and emailConfig.password:
                s.login(emailConfig.username, emailConfig.password )
            s.sendmail(emailConfig.sender, [self.toAddress], msg.as_string())
            s.quit()
            log.debug('Email sent.')
