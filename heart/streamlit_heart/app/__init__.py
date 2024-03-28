import app.home_page
import app.model

#делаем справочную информацию о данных, которые необходимо ввести для прогноза
reference = {'Age': 'Ваш возраст',
'Sex':'Ваш пол',
'ChestPainType':'Тип боли в грудной клетке',
'RestingBP':'Давление крови в покое',
'Cholesterol':'Уровень общего холестерина в крови',
'FastingBS':'Уровень сахара в крови натощак (1, если больше 6,6 мммоль/л и 0 в остальных случаях',
'RestingECG':'результат кардиограммы в покое',
'MaxHR':'максимально достижимый уровень пульса',
'ExerciseAngina':'наличие боли в грудной клетке при физической нагрузке',
'Oldpeak':'oldpeak = ST (Numeric value measured in depression)',
'ST_Slope':'the slope of the peak exercise ST segment (Up: upsloping, Flat: flat, Down: downsloping)'}

image = 'https://images.24ur.com/media/images/1024x576/May2017/e5b28ffeb0_61920351.jpg?v=d41d'
title = "Прогноз риска кардиологического заболевания человека"
