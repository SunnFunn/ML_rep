import app
from app import model, home_page
from app import reference, image, title

import streamlit as st

def main():
    app.home_page.title(title, image)
    app.home_page.sidebar(reference)
    app.home_page.greetings()
    data = app.model.load_data('./app/data/heart.csv')
    input_data = app.home_page.input_data(data)
    model.inference(data, input_data)


if __name__ == '__main__':
    main()
