import requests
import logging
import ssl
import socket
import time
import logging
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from os import environ

load_dotenv('webmonitor.env')
REMOTE_SERVER = environ.get("REMOTE_SERVER", "www.google.com")

http_status_codes = {
    '100': 'Informational: Continue',
    '101': 'Informational: Switching Protocols',
    '102': 'Informational: Processing',
    '200': 'Successful: OK',
    '201': 'Successful: Created',
    '202': 'Successful: Accepted',
    '203': 'Successful: Non-Authoritative Information',
    '204': 'Successful: No Content',
    '205': 'Successful: Reset Content',
    '206': 'Successful: Partial Content',
    '207': 'Successful: Multi-Status',
    '208': 'Successful: Already Reported',
    '226': 'Successful: IM Used',
    '300': 'Redirection: Multiple Choices',
    '301': 'Redirection: Moved Permanently',
    '302': 'Redirection: Found',
    '303': 'Redirection: See Other',
    '304': 'Redirection: Not Modified',
    '305': 'Redirection: Use Proxy',
    '306': 'Redirection: Switch Proxy',
    '307': 'Redirection: Temporary Redirect',
    '308': 'Redirection: Permanent Redirect',
    '400': 'Client Error: Bad Request',
    '401': 'Client Error: Unauthorized',
    '402': 'Client Error: Payment Required',
    '403': 'Client Error: Forbidden',
    '404': 'Client Error: Not Found',
    '405': 'Client Error: Method Not Allowed',
    '406': 'Client Error: Not Acceptable',
    '407': 'Client Error: Proxy Authentication Required',
    '408': 'Client Error: Request Timeout',
    '409': 'Client Error: Conflict',
    '410': 'Client Error: Gone',
    '411': 'Client Error: Length Required',
    '412': 'Client Error: Precondition Failed',
    '413': 'Client Error: Request Entity Too Large',
    '414': 'Client Error: Request-URI Too Long',
    '415': 'Client Error: Unsupported Media Type',
    '416': 'Client Error: Requested Range Not Satisfiable',
    '417': 'Client Error: Expectation Failed',
    '418': 'Client Error: I\'m a teapot',
    '419': 'Client Error: Authentication Timeout',
    '420': 'Client Error: Enhance Your Calm',
    '420': 'Client Error: Method Failure',
    '422': 'Client Error: Unprocessable Entity',
    '423': 'Client Error: Locked',
    '424': 'Client Error: Failed Dependency',
    '424': 'Client Error: Method Failure',
    '425': 'Client Error: Unordered Collection',
    '426': 'Client Error: Upgrade Required',
    '428': 'Client Error: Precondition Required',
    '429': 'Client Error: Too Many Requests',
    '431': 'Client Error: Request Header Fields Too Large',
    '444': 'Client Error: No Response',
    '449': 'Client Error: Retry With',
    '450': 'Client Error: Blocked by Windows Parental Controls',
    '451': 'Client Error: Redirect',
    '451': 'Client Error: Unavailable For Legal Reasons',
    '494': 'Client Error: Request Header Too Large',
    '495': 'Client Error: Cert Error',
    '496': 'Client Error: No Cert',
    '497': 'Client Error: HTTP to HTTPS',
    '499': 'Client Error: Client Closed Request',
    '500': 'Server Error: Internal Server Error',
    '501': 'Server Error: Not Implemented',
    '502': 'Server Error: Bad Gateway',
    '503': 'Server Error: Service Unavailable',
    '504': 'Server Error: Gateway Timeout',
    '505': 'Server Error: HTTP Version Not Supported',
    '506': 'Server Error: Variant Also Negotiates',
    '507': 'Server Error: Insufficient Storage',
    '508': 'Server Error: Loop Detected',
    '509': 'Server Error: Bandwidth Limit Exceeded',
    '510': 'Server Error: Not Extended',
    '511': 'Server Error: Network Authentication Required',
    '598': 'Server Error: Network read timeout error',
    '599': 'Server Error: Network connect timeout error',
}


def isValidURL(str):

    # Regex to check valid URL
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    # Compile the ReGex
    p = re.compile(regex)

    # If the string is empty
    # return false
    if (str == None):
        return False

    # Return if the string
    # matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False


def email_sender(subject, input_message, sender, password, email_to):
    ''' function to send email '''
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = (',').join(email_to)

    # Create the plain-text and HTML version of your message
    text = input_message
    html = f"""\
    <html>
    <body>
        {input_message}
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    user_smptp_host = environ.get('USER_SMTP_HOST', 'smtp.gmail.com')
    user_smptp_port = environ.get('USER_SMTP_PORT', 587)
    with smtplib.SMTP(user_smptp_host, user_smptp_port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender, password)
        try:
            server.sendmail(sender, email_to, message.as_string())
            return True
        except Exception as e:
            return False


def is_connected(hostname):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except:
        pass
    return False


def main(url, mailTo=[], afterEverySeconds=30, skipSSL=False, secondsAfterResendMail=300):
    verify = not skipSSL
    mailTo = mailTo.split(',')
    if(skipSSL):

        ssl._create_default_https_context = ssl._create_unverified_context
    shouldSendMail = True
    secondsUntilLastFailure = 0
    while True:
        if is_connected(REMOTE_SERVER):
            try:
                r = requests.get(url, verify=verify)
                extraMsg = ''
            except Exception as e:
                extraMsg = f'Exception Occured: {e}'
                logger.critical(extraMsg)
                r = False
            if(not r):
                status = 500
            else:
                status = r.status_code

            webMessage = http_status_codes[str(status)]
            msg = f'URL: {url} Status = {status}, Message: {webMessage} \n{extraMsg}'

            print(msg)
            if(status <= 299 and status >= 100):
                logger.debug("Debug: "+msg)
                secondsUntilLastFailure = 0
            else:
                subject = webMessage
                sender = environ.get('EMAIL_SENDER')
                password = environ.get('EMAIL_SENDER_PASSWORD')
                email_to = [sender] + mailTo
                logger.critical("Error: "+msg)
                secondsUntilLastFailure += afterEverySeconds

                if(shouldSendMail):
                    shouldSendMail = False
                    secondsUntilLastFailure = 0
                    if(email_sender(subject, msg, sender, password, email_to)):
                        emailDebugMsg = f"Email sent to {email_to}"
                    else:
                        emailDebugMsg = f'Email not sent to {email_to}'
                else:
                    emailDebugMsg = "Not sending the mail"
                print(emailDebugMsg)
                logger.debug("Debug: "+emailDebugMsg)

                shouldSendMail = (secondsUntilLastFailure >=
                                  secondsAfterResendMail)
            time.sleep(afterEverySeconds)
        else:
            msg = "Not Connected to internet"
            print(msg)
            logger.warning("Warning: "+msg)
            time.sleep(10)


if __name__ == '__main__':

    url = environ.get('URL')
    logfile = environ.get('LOGFILE_NAME', 'webmonitor.log')
    logging.basicConfig(filename=logfile,
                        format='%(asctime)s %(message)s',
                        filemode='a')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if isValidURL(url):
        mailTo = environ.get('MAIL_TO', '')
        checkAfter = int(environ.get('CHECK_AFTER', 30))
        skipSSL = ((environ.get('SKIP_SSL', 'False').lower() == 'true'))
        secondsAfterResendMail = int(environ.get('RESEND_MAIL_AFTER', 300))
        main(url, mailTo, checkAfter, skipSSL, secondsAfterResendMail)
    else:
        msg = f"Invalid URL: {url}"
        logger.debug(msg)
        print(msg)
        exit()
