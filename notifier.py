import requests
import lxml.html
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from bs4 import BeautifulSoup

_username = ""
_password = ""

# Logs in the user and returns the url of the page to which the user is redirected


def login(username, password):
    LOGIN_URL = 'https://sso-prod.sun.ac.za/cas/login?TARGET=http%3A%2F%2Ft2000-05.sun.ac.za%2FEksamenUitslae%2FEksUitslae.jsp%3FpLang%3D1'

    session = requests.session()  # Create a new session
    login = session.get(LOGIN_URL)

    login_html = lxml.html.fromstring(login.text)
    hidden_elements = login_html.xpath('//form//input[@type="hidden"]')
    form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

    login_not_complete = True
    global _username
    global _password

    while login_not_complete:

        # Get username and password from user
        _username = raw_input("Student Number: ")
        _password = raw_input("Password: ")

        # set the form username and password to the ones given by the user
        form['username'] = _username
        form['password'] = _password

        # Attempt login with given credentials
        response = session.post(LOGIN_URL, data=form)

        if(response.url != LOGIN_URL):  # If the user is redirected to the marks page, login was successful
            print("Login Successful\n")
            login_not_complete = False
        else:
            print("Login Failed\n")
    print(response.url)
    return response.url

# Returns the number of non-empty elements in the table


def get_mark_count(table):
    i = 0
    # loop through each row in the table which contains marks
    for tr in table.find_all("tr")[2:]:
        # loop through each column in the table which contains marks
        for td in tr.find_all("td")[2:5]:
            if td.text != "":
                i = i + 1
    return i

# Returns the given table as a string


def get_marks_table(table):
    marks = ""
    for tr in table.find_all("tr")[2:]:
        for td in tr.find_all("td")[1:]:
            marks = marks + td.text + "\t"
        marks = marks + "\n"
    return marks

# Sends email from users student email account to themselve to notify them


def send_notification(table):
    emailaddr = _username + "@sun.ac.za"  # creates email address from the username

    msg = MIMEMultipart()  # Create new message
    msg['From'] = emailaddr
    msg['To'] = emailaddr
    msg['Subject'] = "New Marks Out!"

    # Get table as a string and set the body of the message to it
    body = get_marks_table(table)
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.office365.com', 587)  # Connect to server
    server.starttls()
    server.login(emailaddr, _password)  # Login as the user

    server.sendmail(emailaddr, emailaddr, msg.as_string())  # Send the email
    print(body)  # Output the message sent
    print("Mail sent\n")
    server.quit()  # Disconnect from the server


def main():
    url = login(_username, _password)  # Login as the user
    previous_count = 0  # Initialize the intial number of released marks to zero

    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")  # Get soup from the page

        table = soup.find_all('table')[1]  # Find the first table in the page
        # Get the current number of released marks
        current_count = get_mark_count(table)

        if current_count > previous_count:
            previous_count = current_count
            send_notification(table)

        time.sleep(60)  # Sleep the program for 60 seconds


if __name__ == "__main__":
    main()
