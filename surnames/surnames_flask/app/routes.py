from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import InputForm, LoginForm, RegistrationForm, DataForm
from flask_login import current_user, login_user, logout_user, login_required
from app.tables import User, Surnames
from app.inference import inference, decode_samples

import sqlalchemy as sa
from urllib.parse import urlsplit

import torch
from app.model import classifier, vectorizer

classifier.load_state_dict(torch.load('./app/model/model_surnames_v2.pth'))
classifier.to('cpu')

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html', title = 'Home page')

@app.route('/input', methods=['GET', 'POST'])
@login_required
def input_to_predict():

    form = InputForm()
    if form.validate_on_submit():

        input_text = form.input_text.data
        temperature = float(form.temperature.data)
        samples_number = int(form.samples_number.data)
        predicted_surnames = []

        for _ in range(samples_number):
            indexes = inference(input_text, temperature)
            surname = decode_samples(indexes, vectorizer)[0]
            if surname not in predicted_surnames:
                predicted_surnames.append(surname)

        surnames_info = Surnames(surname_beginning = input_text, surnames_generated=' '.join(predicted_surnames), author=current_user)
        db.session.add(surnames_info)
        db.session.commit()

        return render_template('predictions.html', title = 'Sentiment analisys', predicted_surnames=predicted_surnames)
    return render_template('input.html', title = 'Sentiment analisys', form=form)

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
        if not next_page or urlsplit(next_page).netloc != '':
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
        user = User(username=form.username.data, city=form.city.data, profession=form.profession.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
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
        surnames = db.session.scalars(user.surnames.select()).all()
        return render_template('output.html', title = 'Some analytics', surnames=surnames[-5:], user=input_username)
    return render_template('analytics.html', title = 'Some analytics', form=form)
