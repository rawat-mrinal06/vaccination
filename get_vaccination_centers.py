import email.message
import time
import requests
from datetime import date
import smtplib, ssl
import pandas as pd
import schedule

sender_email = ""	# Sender's Email
mail_subject = ''	# Mail Subeject
password = ""		# Sender's Password
rec = []		# List of recipients email ids 
pincode = 		# Pincode


def send_email(message):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)


        for r in rec:
            # message = "Message_you_need_to_send"
            msg = email.message.EmailMessage()
            msg['Subject'] = mail_subject
            msg['From'] = sender_email
            msg['To'] = r
            # msg.add_header('Content-Type', 'text/html')
            msg.set_content(message, subtype='html')
            # sending the mail
            # print(message)
            server.sendmail(msg['From'], [r], msg.as_string())

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()


def get_vaccine_data():
    try:
        today = date.today()
        d4 = today.strftime("%d-%m-%Y")
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
        URL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}'.format(pincode, d4)
        # print(URL)
        response = requests.get(URL, headers=headers)
        if response.status_code == 200:
            # print('Hitting...')
            data = response.json()
            options_available = []
            for center in data['centers']:
                for session in center['sessions']:
                    if session['min_age_limit'] < 45 and session['available_capacity'] > 0:
                        dct = {'Center Name': center['address'], 'Date': session['date'], 'Capacity Available': session['available_capacity'],
                               'Vaccine': session['vaccine'], 'Slots': session['slots']}
                        options_available.append(dct)

            for o in options_available:
                print(o)
            if options_available:
                df = pd.DataFrame(options_available)
                dfg = df.groupby(['Center Name', 'Date', 'Vaccine']).sum()
            # print(dfg)
                send_email(dfg.to_html())
    except:
        print('API Limit Exceeded. Restart script ')


if __name__ == '__main__':
    # get_vaccine_data()
    schedule.every(30).seconds.do(get_vaccine_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
