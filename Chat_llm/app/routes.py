from app import app
from app.forms import QueryForm
from app import chat

from flask import render_template, redirect, url_for, session


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    title = 'Dating apps reviews analysis'
    session['answer'] = ''
    form = QueryForm()

    if form.validate_on_submit():
        query = form.query.data
        session['answer'] = chat.response(query)
        # answer = answer.split(' ')
        # answer = ' '.join(answer[4:])
        return redirect(url_for('answer'))

    return render_template('home.html', title=title, form=form)


@app.route('/answer', methods=['GET', 'POST'])
def answer():
    title = 'AI answer'
    return render_template('answer.html', title=title, answer=session['answer'])
