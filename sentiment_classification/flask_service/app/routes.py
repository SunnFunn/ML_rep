from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import InputForm, LoginForm, RegistrationForm, DataForm, validate_username
from flask_login import current_user, login_user, logout_user, login_required
from app.tables import User, Text
from app.Client import ModelClient

import sqlalchemy as sa
from urllib.parse import urlsplit

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html', title = 'Home page')

@app.route('/input', methods=['GET', 'POST'])
@login_required
def input_to_predict():

    output = {'love': 'You are in love today!',
                  'anger': 'Do not be so angry!',
                  'joy': 'Joyful and careless as always!',
                  'fear': 'Calm down, everyting is going to be OK!',
                  'surprise': 'Never know what is waiting for you!',
                  'sadness': 'Buck up and do not worry!'}

    form = InputForm()
    model_rpc = ModelClient()

    if form.validate_on_submit():

        sentence = form.input_text.data
        response = model_rpc.call(sentence)

        post = Text(body=sentence, predictions=response, author=current_user)
        db.session.add(post)
        db.session.commit()

        return render_template('predictions.html', title='Sentiment analisys', predictions=response, output=output)
    return render_template('input.html', title='Sentiment analisys', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None:
            flash('Unknown username entered. Please register first!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc == '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        validate_username(form, form.username.data)
    return render_template('register.html', title='Register', form=form)

@app.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    form = DataForm()
    if form.validate_on_submit():
        input_username = form.username.data
        user = db.session.scalar(sa.select(User).where(User.username == input_username))
        if user is None or user.username != current_user.username:
            flash('Unknown username entered or data for you does not exist yet!')
            return redirect(url_for('analytics'))
        posts = db.session.scalars(user.posts.select()).all()
        return render_template('output.html', title = 'Some analytics', posts=posts[-5:], user=input_username)
    return render_template('analytics.html', title = 'Some analytics', form=form)
