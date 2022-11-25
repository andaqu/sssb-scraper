from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config
import smtplib

EMAIL = config("EMAIL")
PASS = config("PASS")

# This function should email two tables to EMAIL: the new posted ideal apartments on the SSSB website and the total ideal apartments (which most likely includes previously scraped ones)
def send_an_email(ideal_apartments, changes):

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(EMAIL, PASS)

    # Change subject title according to primary interests; in this case, the primary interest is whether the new scraped apartments are stemming from Birka
    if ((changes["Area"] == "Birka") & (changes["Type"] == "2 rooms & kitchen")).any():
        subject = "New Birka 2-room apartment/s!"
    elif (changes["Area"] == "Birka").any():
        subject = "New Birka apartment/s!"
    else:
        subject = "New ideal apartments"

    # Make clickable the Address parts of the tables
    def make_clickable(url, name):
        return f"<a href={url}>{name}</a>"

    ideal_apartments["Address"] = ideal_apartments.apply(lambda x: make_clickable(x["Link"], x["Address"]), axis=1)
    changes["Address"] = changes.apply(lambda x: make_clickable(x["Link"], x["Address"]), axis=1)
    
    # The link is only needed to make addresses clickable, drop them before sending email
    ideal_apartments = ideal_apartments.drop(["Link"], axis=1)
    changes = changes.drop(["Link"], axis=1)

    bodyText = ""

    bodyHTML = """\
    <html>
    <head></head>
    <p> New scraped changes are as follows: <p>
    {0}
    <p> Total ideal apartments: <p>
    {1}
    </html>
    """.format(changes.to_html(escape=False), ideal_apartments.to_html(escape=False))

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

    print("Email sent!")