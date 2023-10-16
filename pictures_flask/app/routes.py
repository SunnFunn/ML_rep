from app import app
from app.forms import UploadForm
from app.pictures import main

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from werkzeug.utils import secure_filename

import os

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Григорий'}
    title = 'Поиск разности картинок'
    filenames = os.listdir(app.config['RESULTED_PICTURES_FOLDER'])
    return render_template('index.html', title=title, user=user, filenames=filenames)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	form = UploadForm()
	
	if form.validate_on_submit():
		if len(form.pictures.data) != 2:
			flash('Invalid number of files uploaded')
			return redirect(url_for('upload'))
		else:
			result = main(app.config['FILTER_THRESHOLD'], form.pictures.data[0], form.pictures.data[1])
			result[0].save(os.path.join(app.config['RESULTED_PICTURES_FOLDER'],'result.jpg'))
		return redirect(url_for('index'))
	return render_template('upload.html', form=form)

@app.route('/index/<filename>')
def download(filename):
	return send_from_directory(app.config['RESULTED_PICTURES_FOLDER'], filename)	
