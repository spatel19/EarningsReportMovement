from flask import Flask, render_template, url_for, flash, redirect
import requests, json, urllib.request, time
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
app = Flask(__name__)
from bs4 import BeautifulSoup

url = ("https://finviz.com/screener.ashx?v=161&f=earningsdate_todayafter&o=-marketcap")

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")
firststock = soup.findAll('a', {'class': 'screener-link-primary'})[0].text
secondstock = soup.findAll('a', {'class': 'screener-link-primary'})[1].text
thirdstock = soup.findAll('a', {'class': 'screener-link-primary'})[2].text

app.config['SECRET_KEY'] = '98924a7113635b13fda543163bb92337'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


@app.route("/")
@app.route("/home")
def home():
    firststk = firststock
    secondstk = secondstock
    thirdstk = thirdstock
    return render_template('home.html', firstStock = firststk, secondStock = secondstk, thirdStock = thirdstk)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

if __name__ == "__main__":
    app.run()
