import ConfigParser
from email.mime.text import MIMEText
import smtplib, os
from email.mime.text import MIMEText
from threading import Thread


class EmailConfig:
    '''Class that reads and stores the email server connection properties from a local configuration file.
       
       Example local configuration file cog.cfg:
       
       [email]
       email.server=smtp.gmail.com
       # leave port blank if default
       email.port=
       email.sender=notify_esmf.esrl@noaa.gov
       email.username=<username>
       email.password=<password>
       # optional security, leave blank if not needed
       email.security=STARTTLS
    '''
    
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        
        try:
            
            cog_config_dir = os.getenv('COG_CONFIG_DIR', '/usr/local/cog/cog_config')
            CONFIGFILEPATH = os.path.join(cog_config_dir, 'cog.cfg')
    
            config.read( CONFIGFILEPATH )
            self.server = config.get('email','email.server')
            self.port = config.get('email','email.port')
            self.sender = config.get('email','email.sender')
            self.username = config.get('email','email.username')
            self.password = config.get('email','email.password')
            self.security = config.get('email','email.security')
            print 'Using email server=%s' %  self.server
            print 'Using email port=%s' %  self.port
            print 'Using email sender=%s' %  self.sender
            print 'Using email username=%s' %  self.username
            print 'Using email password=%s' %  self.password
            print 'Using email security=%s' %  self.security
            self.init = True
        except Exception as e:
            print "Email configuration file not found, email notification disabled"
            print e
            self.init = False

# module scope email configuration
emailConfig = EmailConfig()

def notify(toUser, subject, message):
    
    # send email in separate thread, do not wait
    emailThread = EmailThread(toUser.email, subject, message)
    emailThread.start()

def sendEmail(fromAddress, toAddress, subject, message):
    
    # send email in separate thread, do not wait
    emailThread = EmailThread(toAddress, subject, message, fromAddress=fromAddress)
    emailThread.start()

        
class EmailThread(Thread):
    '''Class that sends an email in a separate thread.'''
    
    def __init__ (self, toAddress, subject, message, fromAddress=None):
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
        
    def run(self):
        
        #print "From: %s" % self.fromAddress
        print "To: %s" % self.toAddress
        print "Subject: %s" % self.subject
        print "Message: %s" % self.message
        
        # use local mail server
        #toUser.email_user(subject, message, from_email=fromAddress)
        
        # use email relay server
        if emailConfig.init == True:
    
            # use email relay server
            msg = MIMEText(self.message)
            msg['Subject'] = self.subject
            msg['From'] = self.fromAddress
            msg['To'] = self.toAddress    
            if emailConfig.port is not None:
                s = smtplib.SMTP( emailConfig.server, emailConfig.port )
            else:
                s = smtplib.SMTP( emailConfig.server )
            if emailConfig.security=='STARTTLS':
                s.starttls()
            if emailConfig.username and emailConfig.password:
                s.login(emailConfig.username, emailConfig.password )
            s.sendmail(emailConfig.sender, [self.toAddress], msg.as_string())
            s.quit()
            print 'Email sent.'
