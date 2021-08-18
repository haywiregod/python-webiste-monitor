# Python Website Monitor
Logs the status of a URL and can send email if any error occurs on that URL

## Requirements
First install all requirements via `pip install -r requirements.txt`

## Settings
1. Create a copy of the env.example as webmonitor.env
2. In webmonitor.env
    1. `URL` = "YOUR URL HERE eg: www.github.com"
    2. `CHECK_AFTE`R = After how many seconds the url should be checked again
    3. `RESEND_MAIL_AFTER` = If an error occurs and mail is sent, after how many seconds should the mail be sent again
    4. `LOGFILE_NAME` = Name of the logfile to be generated
    5. `USER_SMTP_HOST` = smtp host, default is smtp.gmail.com
    6. `USER_SMTP_PORT` =  smtp port, default is 587
    7. `EMAIL_SENDER` = Your Email address from which email will be sent
    8. `EMAIL_SENDER_PASSWORD` = Password of `EMAIL_SENDER`
    9. `REMOTE_SERVER` = URL to check if the script can access internet, default is www.google.com
    10. `MAIL_TO` =  Comma seprated email addresses to which error email will be sent. Eg: abc@exaple.com,efg@example.com. Please note, error email is always sent to the `EMAIL_SENDER`
    11. `SKIP_SSL` = Default is False, make it True if you want to skip ssl check

## How to Run?
After making the changes to `webmonitor.env` simply run `python webmonitor.py`
