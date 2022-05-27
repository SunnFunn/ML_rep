from flask import render_template, flash, redirect, url_for, jsonify
from app import app
from app.forms import StringForm
import numpy as np

import torch
from app.model import classifier, vectorizer

#classifier.load_state_dict(torch.load('C:/Users/Алексей Третьяков/Desktop/Sentiment_analysis/app/model/model.pth'))
classifier.load_state_dict(torch.load('./app/model/model.pth'))
classifier.to('cpu')

@app.route('/')
def status():
	return jsonify({'status': 'ok'})


@app.route('/input_text', methods=['GET', 'POST'])
def input_text():
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
            
        #return redirect('/input_text')
        return render_template('predictions.html', title = 'Sentiment analisys', predictions=predictions)
    return render_template('input_text.html', title = 'Sentiment analisys', form=form)

#if __name__ == '__main__':
#    app.run(host = MODEL_HOST, port = MODEL_PORT)
