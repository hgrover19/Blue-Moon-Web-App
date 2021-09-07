from flask import Flask, render_template
from flask import request
from celery import Celery
import gspread
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import re
import os
from datetime import datetime


app = Flask(__name__,template_folder='template')
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


emailAddress = "blue.moon.music.bot@gmail.com"
emailPass = "bluemoonmusicbotaccount#lessonsforcharity"
s = smtplib.SMTP(host='smtp.gmail.com', port=587)
s.starttls()
s.login(emailAddress,emailPass)

# Gain access to data in spreadsheet
gc = gspread.service_account(filename='keys.json')
sh = gc.open('BM Master Data')
sheet = sh.get_worksheet(0)
sheet2 = sh.get_worksheet(1)
sheet3 = sh.get_worksheet(2)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',title='Home')

@app.route("/about-us")
def aboutUs():
    return render_template('aboutUs.html',title='About Us')

@app.route("/registration")
def registration():
    return render_template('registration.html',title='Registration')

@app.route("/tutor-registration")
def tutorReg():
    return render_template('tutorReg.html',title='Tutor Registration')

@app.route("/student-registration")
def register():
    return render_template('studentReg.html',title='Student Registration')

@app.route("/registered",methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        studentName = request.form.get("studentName")
        studentGrade = request.form.get("studentGrade")
        emailContact = request.form.get("emailContact")
        instrument = request.form.get("instrument")
        insFig(studentName,studentGrade,emailContact,instrument)
        return render_template("registered.html",title="Registered!")
    
    
@celery.task
def insFig(studentName,studentGrade,emailContact,instrument):
    def read_template(filename):
        with open(filename,'r',encoding='utf-8') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)

    max_rows = len(sheet.get_all_values()) - 1 # number of used rows
    instrumentMatches = [] # double list (2nd set is of tutor info) to hold tutors that match instrument
    for i in range(1,max_rows+2):
        if sheet.cell(i, 2).value == instrument:
            instrumentMatches.append(sheet.row_values(i))

    def tutorFinder(instrumentMatches):
        tutors = []
        for i in range(len(instrumentMatches)):
            tutors.append(instrumentMatches[i][3])
        mini = min(tutors)
        return tutors.index(mini) # returns index in 'instrumentMatches'
    def tutorFilter(instrumentMatches):
        removalIndexes = []
        for i in range(len(instrumentMatches)):
            cell_row = sheet.find(instrumentMatches[i][5])
            row = cell_row.row
            if sheet.cell(row,7).value != 'Active' or sheet.cell(row,3).value == sheet.cell(row,6).value:
                removalIndexes.append[i]
        if removalIndexes != 0:
            for i in removalIndexes:
                del instrumentMatches[i]
        
    def emailToStudentNegative():
        message_template = read_template('studentMessageNegative.txt')
        msg = MIMEMultipart()
        message = message_template.safe_substitute(STUDENT_NAME=studentName,INSTRUMENT=instrument)
        msg['From'] = emailAddress
        msg['To'] = emailContact
        msg['Subject'] = "Tutor Unavaliable"
        msg.attach(MIMEText(message,'plain'))
        s.send_message(msg)
    def adminEmailNegative():
        message_template = read_template('negativeEmail.txt')
        msg = MIMEMultipart()
        message = message_template.safe_substitute(STUDENT_NAME=studentName,STUDENT_GRADE=studentGrade,INSTRUMENT=instrument,EMAIL_CONTACT=emailContact)
        msg['From'] = emailAddress
        msg['To'] = 'bluemoonmusic@mtsd.us'
        msg['Subject'] = "Tutor Unavaliable"
        msg.attach(MIMEText(message,'plain'))
        s.send_message(msg)
    

    tutorFilter(instrumentMatches)

    if len(instrumentMatches) != 0:
        found = tutorFinder(instrumentMatches)
        tutorName = instrumentMatches[found][0]
        tutorEmail = instrumentMatches[found][4]
        def emailToStudent():
            message_template = read_template('studentMessage.txt')
            msg = MIMEMultipart()
            message = message_template.safe_substitute(STUDENT_NAME=studentName,INSTRUMENT=instrument,TUTOR_NAME=tutorName,TUTOR_EMAIL=tutorEmail)
            msg['From'] = emailAddress
            msg['To'] = emailContact
            msg['Subject'] = "Tutor Assigned!"
            msg.attach(MIMEText(message,'plain'))
            s.send_message(msg)

        def emailToTutor():
            message_template = read_template('tutorMessage.txt')
            msg = MIMEMultipart()
            message = message_template.safe_substitute(TUTOR_NAME=tutorName,INSTRUMENT=instrument,STUDENT_NAME=studentName,STUDENT_GRADE=studentGrade,STUDENT_EMAIL=emailContact)
            msg['From'] = emailAddress
            msg['To'] = tutorEmail
            msg['Subject'] = "Student Assigned!"
            msg.attach(MIMEText(message,'plain'))
            s.send_message(msg)



        def tutorSheetUpdate(found):
            row = sheet.find(tutorName).row
            val = sheet.cell(row,3).value
            val = int(val)
            val+=1
            val = str(val)
            sheet.update_cell(row,3,val)
        #Updates the values in the student sheet to match changes
        def studentSheetUpdate():
            vals = len(sheet2.get_all_values()) + 1
            sheet2.update_cell(vals,1,studentName)
            sheet2.update_cell(vals,2,instrument)
            sheet2.update_cell(vals,3,tutorName)
            sheet2.update_cell(vals,4,studentGrade)
            sheet2.update_cell(vals,5,emailContact)
            sheet2.update_cell(vals,6,'Active')

        def AppDataLogger():
            vals = len(sheet3.get_all_values()) + 1
            now = datetime.now()
            dateTimeStr = now.strftime("%m/%m/%y %H:%M:%S")
            sheet3.update_cell(vals,1,dateTimeStr)
            sheet3.update_cell(vals,2,studentName)
            sheet3.update_cell(vals,3,emailContact)
            sheet3.update_cell(vals,4,instrument)
            sheet3.update_cell(vals,5,tutorName)
            sheet3.update_cell(vals,6,tutorEmail)
            sheet3.update_cell(vals,7,'Success!')

        emailToStudent()
        emailToTutor()
        tutorSheetUpdate(found)
        studentSheetUpdate()
        AppDataLogger()
    else:
        emailToStudentNegative()
        adminEmailNegative()
        def AppDataLogger2():
            vals = len(sheet3.get_all_values()) + 1
            now = datetime.now()
            dateTimeStr = now.strftime("%m/%m/%y %H:%M:%S")
            sheet3.update_cell(vals,1,dateTimeStr)
            sheet3.update_cell(vals,2,studentName)
            sheet3.update_cell(vals,3,emailContact)
            sheet3.update_cell(vals,4,instrument)
            sheet3.update_cell(vals,5,'N/A')
            sheet3.update_cell(vals,6,'N/A')
            sheet3.update_cell(vals,7,'Tutor Unavaliable')
        def studentSheetUpdate2():
            vals = len(sheet2.get_all_values()) + 1
            sheet2.update_cell(vals,1,studentName)
            sheet2.update_cell(vals,2,instrument)
            sheet2.update_cell(vals,3,'N/A')
            sheet2.update_cell(vals,4,studentGrade)
            sheet2.update_cell(vals,5,emailContact)
            sheet2.update_cell(vals,6,'Tutor Unavaliable')
        AppDataLogger2()
        studentSheetUpdate2()

if __name__ == '__main__':
    app.run(debug=True)
    