from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import cgi
from selenium import webdriver
import time
from subprocess import call
from datetime import datetime
import libscrc
import bluepy
import sys

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://kiosk:kiosk123@localhost/kiosk'
db=SQLAlchemy(app)
conn = psycopg2.connect(user="kiosk", password="kiosk123", host="127.0.0.1", port="5432", database="kiosk")
cur = conn.cursor()
count=0
now = datetime.now()
opid=0
urid=0
deviceid=0
user_info=0
patient_records=0
SPO2=0
HR=0
PI=0
date=0
time=0
class Operater(db.Model):

    __tablename__="operater"
    opid=db.Column(db.Integer, primary_key=True)
    name_=db.Column(db.String(20))
    username_=db.Column(db.String(20), unique=True)
    email_=db.Column(db.String(120), unique=True)
    password_=db.Column(db.String(16), unique=True)
    
    def __init__(self, name_, username_, email_, password_):
        self.name_=name_
        self.username_=username_
        self.email_=email_
        self.password_=password_
    
class Users(db.Model):
    __tablename__="users"
    urid=db.Column(db.Integer, primary_key=True)
    urfirstname=db.Column(db.String(20))
    urlastname=db.Column(db.String(20), unique=True)
    urdob=db.Column(db.Date)
    uremail=db.Column(db.String(120), unique=True)
    urphone=db.Column(db.String(10), unique=True)
    urhight=db.Column(db.String(3))
    def __init__(self,urfirstname,urlastname,urdob,uremail,urphone,urhight):
        self.urfirstname=urfirstname
        self.urlastname=urlastname
        self.urdob=urdob
        self.urphone=urphone
        self.uremail=uremail
        self.urhight=urhight

class Logdata(db.Model):
    __tablename__="logdata"
    id=db.Column(db.String(10), primary_key=True)
    username=db.Column(db.String(20), unique=True)
    date=db.Column(db.Date)
    time=db.Column(db.Time)

    def __init__(self,id,username,date,time):
        self.id=id
        self.username=username
        self.date=date
        self.time=time

class Device(db.Model):
    __tablename__="device"
    deviceid=db.Column(db.Integer, primary_key=True)
    macaddress=db.Column(db.String(17), unique=True)
    devicename=db.Column(db.String(30))
    uuid=db.Column(db.String(37), unique=True)
    
    def __init__(self, macaddress, devicename, uuid):
        self.macaddress=macaddress
        self.devicename=devicename
        self.uuid=uuid

class Reading(db.Model):
    __tablename__="reading"
    readingid=db.Column(db.Integer, primary_key=True)
    date=db.Column(db.Date)
    time=db.Column(db.Time)
    opid=db.Column(db.Integer)
    urid=db.Column(db.Integer)
    deviceid=db.Column(db.Integer)
    vsdn=db.Column(db.Integer)
    readingdata=db.Column(db.String(20))
    
    def __init__(self, date, time, opid, urid, deviceid, vsdn, readingdata):
        self.date=date
        self.time=time
        self.opid=opid
        self.urid=urid
        self.deviceid=deviceid
        self.vsdn=vsdn
        self.readingdata=readingdata

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashbord", methods=['GET', 'POST'])
def dashbord():
    autusername=request.form["username"]
    autpsw=request.form["psw"]
    cur.execute("SELECT * FROM operater WHERE username_='" + autusername + "' and password_='" + autpsw +"'")
    autdata = cur.fetchone()
    global opid
    opid = autdata[0]
    if autdata is None:
        flash("*Username or Password is wrong*", "info")
        return redirect(url_for("index"))
    else:
        cur.execute("SELECT urfirstname FROM users order by urfirstname")
        userDropdown =[]
        for i in cur.fetchall():
            userDropdown.extend(i)
        if userDropdown is None:
            return render_template('dashbord.html')
            
        else:
            return render_template('dashbord.html', userDropdown=userDropdown)

@app.route("/dashbordreturn", methods=['GET', 'POST'])
def dashbordreturn():
    cur.execute("SELECT urfirstname FROM users order by urfirstname")
    userDropdown = cur.fetchone()
    return render_template("dashbord.html", userDropdown=userDropdown)

@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template("register.html")

@app.route("/regsuccess", methods=['GET', 'POST'])
def regsuccess():
    if request.method=='POST':
        op_name=request.form["opname"]
        op_username=request.form["opusername"]
        op_email=request.form["opemail"]
        op_psw=request.form["oppsw"]
        op_reppsw=request.form["oppsw-repeat"]
        if op_psw == op_reppsw:
            opdata=Operater(op_name,op_username,op_email,op_psw)
            db.session.add(opdata)
            db.session.commit()
            return render_template("regsuccess.html")
        else:
            flash("Password is not matching*", "info")
            return redirect(url_for("register"))

@app.route("/userregister", methods=['GET', 'POST'])
def userregister():
    return render_template("userregister.html")

@app.route("/userregsuccess", methods=['GET', 'POST'])
def userregsuccess():
    ur_fname=request.form['urfname']
    ur_lname=request.form['urlname']
    ur_dob=request.form['urdob']
    ur_email=request.form['uremail']
    ur_phone=request.form['urphone']
    ur_hight=request.form['urhight']
    urdata=Users(ur_fname, ur_lname,ur_dob,ur_email,ur_phone,ur_hight)
    db.session.add(urdata)
    db.session.commit()
    return render_template("userregsuccess.html")



@app.route("/dashbordrecord", methods=['GET','POST'])
def dashbordrecord():
    #if request.method == 'POST':
    select = request.form.get('urfirstname')
    print(select)
    #form = cgi.FieldStorage()
        #dropusername=form.getvalue('urfirstname');
    cur.execute("SELECT urid,urfirstname,urlastname,urdob,urhight from users where urfirstname='"+ select +"'")
    global user_info
    user_info=cur.fetchone()
    global urid
    urid = user_info[0]
    global deviceid
    deviceid = 1
    
    
    #return render_template("dashbordrecord.html",record=record)
    
    return render_template("dashbordrecord.html", user_info=user_info)
    #else:
     #   return render_template("dashbordrecord.html")
@app.route("/patient_record", methods=['GET','POST'])
def patient_record():
    vs = request.args.get('record')
    #vs = record
    cur.execute("SELECT * FROM reading WHERE urid='"+ str(urid) +"' and vsdn='"+ vs +"'")
    global patient_records
    patient_records=cur.fetchall()
    return render_template("patientrecord.html", user_info=user_info, patient_records=patient_records)

@app.route("/scanning_data", methods=['GET','POST'])
def scanning_data():
    import pc60fw 
    pc60fw.pulseoximeter()
    pc60fwData = pc60fw.data_avg
    global SPO2, HR, PI
    SPO2 = round(pc60fwData[0],2)
    HR = round(pc60fwData[1], 2)
    PI = round(pc60fwData[2],2)
    
    flash("*Remove Finger*","info")
    global date, time
    date = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")
    
    return render_template("scan.html",user_info=user_info, date=date, time=time, HR=HR, SPO2=SPO2, PI=PI)

@app.route("/data_store", methods=['GET', 'POST'])
def data_store():
    #Spo2
    
    spo2vs = ('SPO2')
    readingData=Reading(date, time, opid, urid, deviceid, spo2vs, SPO2)
    db.session.add(readingData)
    db.session.commit()
    
    hrvs = ('HR')
    readingData=Reading(date, time, opid, urid, deviceid, hrvs, HR)
    db.session.add(readingData)
    db.session.commit()
    
    pivs = ('PI')
    readingData=Reading(date, time, opid, urid, deviceid, pivs, PI)
    db.session.add(readingData)
    db.session.commit()
    
    print("Data Saved")
    
    return render_template("dashbordrecord.html", user_info=user_info, date=date, time=time, HR=HR, SPO2=SPO2, PI=PI)

if __name__ == "__main__":
    app.run(debug=True)
