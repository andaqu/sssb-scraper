from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config
import smtplib

EMAIL = config('EMAIL')
PASS = config('PASS')

def send_an_email(df):

    df = df.drop(["index"], axis=1)
    print(df)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(EMAIL, PASS)

    subject = "Change in ideal apartment listing!"
    bodyText = ""

    bodyHTML = """\
    <html>
    <head></head>
    <body>
        {0}
    </body>
    </html>
    """.format(df.to_html())

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL
    message["To"] = EMAIL

    part1 = MIMEText(bodyText, "plain")
    part2 = MIMEText(bodyHTML, "html")

    message.attach(part1)
    message.attach(part2)

    server.sendmail(
        EMAIL,
        EMAIL,
        message.as_string()
    )