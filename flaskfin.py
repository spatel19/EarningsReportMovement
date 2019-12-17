from flask import Flask, render_template, url_for, flash, redirect, session, request
import requests, json, urllib.request, time
from forms import RegistrationForm, LoginForm
app = Flask(__name__)
from bs4 import BeautifulSoup
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pprint import pprint
from bson.son import SON
from datetime import date, time, timedelta
import datetime
import os
from cred import mongoConnectionString, API_KEY


url = ("https://finviz.com/screener.ashx?v=161&f=earningsdate_todayafter&o=-marketcap")

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

try:
    firststock = soup.findAll('a', {'class': 'screener-link-primary'})[0].text
    secondstock = soup.findAll('a', {'class': 'screener-link-primary'})[1].text
    thirdstock = soup.findAll('a', {'class': 'screener-link-primary'})[2].text
except:
    firststock = "AAPL"
    secondstock = "GOOG"
    thirdstock = "AMZN"

app.config['SECRET_KEY'] = '98924a7113635b13fda543163bb92337'

class Connect(object):
    @staticmethod
    def get_connection():
        return MongoClient(mongoConnectionString)

connection = Connect.get_connection()

db = connection.test

data = db.stocks.find_one()

stocksindb = []
for key in data:
    stocksindb.append(key)
    print(key)

if (firststock not in stocksindb) or (secondstock not in stocksindb) or (thirdstock not in stocksindb):
    db.stocks.replace_one({"_id": db.stocks.find_one()["_id"]}, {
    firststock: 0,
    secondstock: 0,
    thirdstock: 0
    })
    print("Hit")

@app.route("/")
@app.route("/home")
def home():
    firststk = firststock
    secondstk = secondstock
    thirdstk = thirdstock
    firstcount = db.stocks.find_one()[firststock]
    secondcount = db.stocks.find_one()[secondstock]
    thirdcount = db.stocks.find_one()[thirdstock]

    if session.get("email"):
        loggedin = True
    else:
        loggedin = False
    return render_template('home.html', firstStock = firststk, secondStock = secondstk, thirdStock = thirdstk, loggedIn = loggedin,
     firstCount=firstcount, secondCount=secondcount, thirdCount=thirdcount, apiKey=API_KEY)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.user.find_one({"email": form.email.data}) or db.user.find_one({"username": form.username.data}):
            flash(f'Username or email is already being used, please try again!',category='warning')
            print("EMAIL exists")
            return render_template('register.html', title='Register', form=form)
        db.user.insert_one({
        "username": form.username.data,
        "email": form.email.data,
        "password": form.password.data,
        "dayVoted": "0"
        })
        session["email"] = form.email.data
        # flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('vote'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(db.user.find_one({"email": form.email.data})["email"])
        if (form.email.data == db.user.find_one({"email": form.email.data})["email"]) and (form.password.data == db.user.find_one({"password": form.password.data})["password"]):
            session["email"] = form.email.data
            return redirect(url_for('vote'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/vote", methods=['GET', 'POST'])
def vote():
    firststk = firststock
    secondstk = secondstock
    thirdstk = thirdstock
    currentDate = date.today().strftime("%j")
    if not session.get("email"):
        return redirect(url_for('home'))
    else:
        if((db.user.find_one({"email": session.get('email')})["dayVoted"]) == currentDate):
            VotedToday = True
            return render_template('vote.html', firstStock = firststk, secondStock = secondstk, thirdStock = thirdstk, votedToday=VotedToday)
        else:
            VotedToday = False
        if request.method == 'POST':
            mongoID = db.user.find_one({"email": session.get('email')})["_id"]
            db.user.update({"_id": mongoID}, {"$set":
            {
            "vote": request.form['stock'],
            "dayVoted": currentDate,
            }})

            db.stocks.update({"_id": db.stocks.find_one()["_id"]}, {"$inc":
            {request.form['stock']: 1}})


    return render_template('vote.html', firstStock = firststk, secondStock = secondstk, thirdStock = thirdstk, votedToday=VotedToday)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    print("LOGOUT")
    session.pop('email', None)
    flash('You were logged out', 'success')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(port=33507)
