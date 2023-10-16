import streamlit as st

#формируем заголовок
def title(title, image):
	#пишем заголовок и оформляем страницу тематической картинкой
	st.title(title)
	st.image(image)

#формируем боковую панель
def sidebar(reference):
	#выводим справочную информацию о значениях и диапазонах входных данных на боковую панель
	st.sidebar.markdown('**Словарь данных о пациентах:**')
	for key,value in reference.items():
		st.sidebar.markdown(f'**{key}**: {value}')

#пишем приветствие
def greetings():
	#Приветствие и небольшая инструкция к заполнению входных данных
	st.markdown('**Здравствуйте, необходимо ввести свои медцинские данные для оценки риска кардиологического заболевания.**')
	st.markdown('```В случае возникновения вопросов с введением данных пользуйтесь справочником на панели слева.```')

#создаем вводные формы и словарь входных данных для получения прогноза на их основе
def input_data(data):
	
	#задаем явно список численных признаков
	nums = ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak']
	
	#формируем словарь с входными данными через диалоговые окна и бегунки
	input_data = {}
	for col in data.columns[:-1]:
		if col in nums:
			st.subheader(f'Выберете ваши данные {col}')
			col_range = range(int(data[col].min()),int(data[col].max()))
			input_data[col] = st.select_slider('выберете значение из диапазона', options=col_range, value=int(data[col].mean()))
		elif col == 'FastingBS':
			st.subheader(f'Выберете ваши данные {col}')
			input_data[col] = st.selectbox('выберете значение из списка', [0,1])
		else:
			st.subheader(f'Выберете ваши данные {col}')
			input_data[col] = st.selectbox('выберете значение из списка', data[col].unique())
	
	return input_data
