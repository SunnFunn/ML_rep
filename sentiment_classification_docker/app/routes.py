from flask import render_template, flash, redirect, url_for, jsonify
from app import app
from app.forms import StringForm
from config import Config
import numpy as np

import torch
from app.model import classifier, vectorizer

classifier.load_state_dict(torch.load('./app/model/model.pth'))
classifier.to('cpu')

@app.route('/home')
def home():
	return render_template('home.html', title = 'Sentiment analisys')


@app.route('/input', methods=['GET', 'POST'])
def input_to_predict():
    form = StringForm()
    
    if form.validate_on_submit():
        text = form.input_text.data
        flash('Text to classify: {}'.format(text))
        
        vectorized_text = \
        torch.tensor(vectorizer.vectorize(text, vector_length=100))
        result = classifier(vectorized_text.unsqueeze(0), apply_softmax=True)
        probability_values, indices = result.max(dim=1)
        predicted_category = vectorizer.category_vocab.lookup_index(indices.item())
        
        predictions = predicted_category
       #'probability': np.round(probability_values.item(),2)}
        output = {'love': 'You are in love today!',
                  'anger': 'Do not be so angry!',
                  'joy': 'Joyful and careless as always!',
                  'fear': 'Calm down, everyting is going to be OK!',
                  'surprise': 'Never know what is waiting for you!',
                  'sadness': 'Buck up and do not worry!'}
                  
        return render_template('predictions.html', title = 'Sentiment analisys',
                                predictions=predictions, output=output)
    return render_template('input.html', title = 'Sentiment analisys', form=form)
