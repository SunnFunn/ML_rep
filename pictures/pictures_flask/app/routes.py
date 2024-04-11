from typing import Dict, Any
from urllib.parse import urlsplit

from app import app, db
from app.forms import UploadForm, SettingForm, LoginForm, RegistrationForm
from app.pictures import partitioning, join_jpeg, compare
from app.pages_aligning import pages_align

from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.db_tables import User, Pdfs

from flask import render_template, flash, redirect, url_for, request, send_from_directory, send_file, session, abort
from werkzeug.utils import secure_filename

import sys
import os
import io
import uuid
import shutil
import time
import numpy as np
import multiprocessing as mp
from PIL import ImageFilter

inputs_default = app.config['INPUTS_DEFAULT']

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    ............................................
.............................

    return render_template('home.html', title=title, form=form, page_numbers_list=page_numbers_list, dict_out=dict_out,
                           data=(inputs[4], inputs[7], inputs[9]))

@app.route('/doc1')
@login_required
def doc1():
    basedir = os.path.abspath(os.path.dirname(__file__))
    outputs = os.path.join(basedir, 'static/outputs/')
    fname1 = session['path1']
    return send_from_directory(outputs, fname1, as_attachment=True, download_name='result1.pdf')

@app.route('/doc2')
@login_required
def doc2():
    basedir = os.path.abspath(os.path.dirname(__file__))
    outputs = os.path.join(basedir, 'static/outputs/')
    fname2 = session['path2']
    return send_from_directory(outputs, fname2, as_attachment=True, download_name='result2.pdf')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    filter_options = ['EDGE_ENHANCE', 'EDGE_ENHANCE_MORE', 'SMOOTH', 'SMOOTH_MORE', 'SHARPEN', 'DETAIL', 'FIND_EDGES', 'BLUR']

    filter_options_dict = {'EDGE_ENHANCE': ImageFilter.EDGE_ENHANCE, 'EDGE_ENHANCE_MORE': ImageFilter.EDGE_ENHANCE_MORE,
                            'SMOOTH': ImageFilter.SMOOTH, 'SMOOTH_MORE': ImageFilter.SMOOTH_MORE, 'SHARPEN': ImageFilter.SHARPEN,
                            'DETAIL': ImageFilter.DETAIL, 'FIND_EDGES': ImageFilter.FIND_EDGES, 'BLUR': ImageFilter.BLUR}
    filter_options_dict_swapped = dict((v, k) for k, v in filter_options_dict.items())

    form = SettingForm()
    form.select_filter.choices = filter_options
    form.select_thresh.data = inputs_default[0]
    form.select_kernel_w.data = inputs_default[1][0]
    form.select_kernel_h.data = inputs_default[1][1]
    form.select_iterations.data = inputs_default[2]
    form.select_filter.data = filter_options_dict_swapped[inputs_default[3]]
    form.select_blend.data = inputs_default[4]
    form.select_dpi.data = inputs_default[5]

    if form.validate_on_submit():

        .............................................

    return render_template('settings.html', title='Параметры', form=form, data=inputs_default)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.username.data in app.config['ALLOWED_USERS']:
            user = User(username=form.username.data, email=form.email.data, city=form.city.data,
                        company=form.company.data, profession=form.profession.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация прошла успешно!')
            return redirect(url_for('login'))
        else:
            flash('Вы не авторизованный для регистрации пользователь!')
            return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(413)
def too_large(e):
    error_message_413 = "Ошибка 413, один или несколько файлов превысили лимит в 10МБ"
    return render_template('errors.html', title='что-то пошло не так', error_message_413 = error_message_413, e=e), 413

@app.errorhandler(404)
def not_found_error(e):
    error_message_404 = "Ошибка 404, страница или данные не найдены"
    return render_template('errors.html', title='что-то пошло не так', error_message_404 = error_message_404, e=e), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    error_message_500 = "Ошибка 500, сервер не может обработать ваш запрос, обратитесь к администратору"
    return render_template('errors.html', title='что-то пошло не так', error_message_500 = error_message_500, e=e), 500
