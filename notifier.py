import requests
import lxml.html
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from bs4 import BeautifulSoup

_username = ""
_password = ""

def login(username, password):
    LOGIN_URL = 'https://sso-prod.sun.ac.za/cas/login?TARGET=http%3A%2F%2Ft2000-05.sun.ac.za%2FEksamenUitslae%2FEksUitslae.jsp%3FpLang%3D1'

    session = requests.session()
    login = session.get(LOGIN_URL)

    login_html = lxml.html.fromstring(login.text)
    hidden_elements = login_html.xpath('//form//input[@type="hidden"]')
    form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

    login_not_complete = True
    global _username
    global _password

    while login_not_complete:

        _username = raw_input("Student Number: ")
        _password = raw_input("Password: ")

        form['username'] = _username
        form['password'] = _password

        response = session.post(LOGIN_URL, data=form)

        if(response.url != LOGIN_URL):
            print "Login Successful\n"
            login_not_complete = False
        else:
            print "Login Failed\n"

    return response.url

def get_mark_count(table):
    i = 0
    for tr in table.find_all("tr")[2:]:
        for td in tr.find_all("td")[2:5]:
            if td.text != "":
                i = i + 1
    return i

def get_marks_table(table):
    marks = ""
    for tr in table.find_all("tr")[2:]:
        for td in tr.find_all("td")[1:]:
            marks = marks + td.text + "\t"
        marks = marks + "\n"
    return marks

def send_notification(table):
    emailaddr = _username + "@sun.ac.za"

    msg = MIMEMultipart()
    msg['From'] = emailaddr
    msg['To'] = emailaddr
    msg['Subject'] = "New Marks Out!"

    body = get_marks_table(table)
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(emailaddr, _password)

    server.sendmail(emailaddr, emailaddr, msg.as_string())
    print body
    print "Mail sent\n"
    server.quit()

url = login(_username, _password)

previous_count = 0

while True:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    table = soup.find_all('table')[1]
    current_count = get_mark_count(table)

    if current_count > previous_count:
        previous_count = current_count
        send_notification(table)

    time.sleep(60)
