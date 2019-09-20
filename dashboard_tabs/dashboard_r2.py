import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from import_dataset import excel_file_dec2018, excel_file_winter, excel_file_repair
from datetime import datetime as dt
import pandas as pd
import numpy as np
import os 

# GETTING AND CLEANING DATA

# KIO @Risk is made-up number (average of KIO Fact)
# KTG @Risk is made-up number
a_data = {
    'Участок': ["Аппак", "Жалпак", "СП Инкай-1", "СП Инкай-2", "СП Инкай-3", "СП Инкай-R", "Буденовское", "Орталык", "ПВ-19"],
    'КИО Факт': [0, 62, 50, 52, 33, 88, 73, 100, 12],
    "КИО @Risk": [52.2, 52.2, 52.2, 52.2, 52.2, 52.2, 52.2, 52.2, 52.2],
    'КТГ Факт': [100, 100, 100, 100, 100, 100, 100, 100, 100],
    'КТГ @Risk': [50, 50, 50, 50, 50, 50, 50, 50, 50]
}

a_df = pd.DataFrame(a_data)

# "Факт" is made-up number (average)
# First datapoint 16.75 of Tech Limit is made-up (average of the rest)
p_data = {
    'Участок': ["Аппак", "Жалпак", "СП Инкай-1", "СП Инкай-2", "СП Инкай-3", "СП Инкай-R", "Буденовское", "Орталык", "ПВ-19"],
    'Норма': [3.39, 16.95, 2.17, 13.13, 5.49, 8, 6.1, 2.86, 3.32],
    'Факт': [6.82, 6.82, 6.82, 6.82, 6.82, 6.82, 6.82, 6.82, 6.82],
    '@Risk': [35.1, 4.61, 5.98, 4.13, 3.99, 6.38, 8.63, 8.93, 10.39],
    "Тех лимит": [16.75, 12.17, 9.74, 11.77, 10.59, 34.96, 23.32, 10.28, 18.77]
}

p_df = pd.DataFrame(p_data)

# totally made-up data
q_data = {
    'Участок': ["Аппак", "Жалпак", "СП Инкай-1", "СП Инкай-2", "СП Инкай-3", "СП Инкай-R", "Буденовское", "Орталык", "ПВ-19"],
    'Факт': [7, 7, 7, 7, 7, 7, 7, 7, 7],
    "План @Risk": [8, 8, 8, 8, 8, 8, 8, 8, 8],
    "Факт (Норма)": [8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2],
    "План @Risk (Норма)": [7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2]
}

q_df = pd.DataFrame(q_data)


table_data = {
    'Показатели': ["Опер. прибыль", "Доходы", "Себестоимость", "План [скв]", "Факт [скв]", "План @Risk [скв]", "Турбо-план [скв]", "Кол-во бур план [ед]", "Кол-во бур факт [ед]", "Кол-во бур @Risk"],
    "Аппак": [0,0,0,0,1,0,0,0,0,0],
    "Жалпак": [0,0,0,0,13,0,0,0,8.24,0],
    "СП Инкай-1": [-2669936, 31007589, 33677525, 0, 9, 0, 0, 0, 4.89, 0],
    "СП Инкай-2": [-5417536, 39517982, 44935518, 33,20,0,0,0,8.42,0],
    "СП Инкай-3": [-5317686, 25616157, 30933844,6,15,0,0,0,6.32,0],
    "СП Инкай-R": [0,0,0,0,36,0,0,0,6.32,0],
    "Буденовское": [11820447,54037500,42217053,39,11,0,0,0,6.32,0],
    'Орталык': [1382674,10047121,8664447,16,3,0,0,0,2.29,0],
    "ПВ-19": [0,0,0,16,0,0,0,0,4.26,0]
}

table_df = pd.DataFrame(table_data)

# EXTRACTING VARIABLES FOR SIMPLICITY
areas_list = ["Аппак", "Жалпак", "СП Инкай-1", "СП Инкай-2", "СП Инкай-3", "СП Инкай-R", "Буденовское", "Орталык", "ПВ-19"]

# BLOCK WITH SLIDERS
dashboard_r2_sliders = html.Div(children = [
    html.Div(
        dcc.DatePickerRange(
            id = 'date-picker-range-r2',
            month_format = 'DD.MM.YYYY',
            display_format = 'DD.MM.YYYY', 
            with_portal = True,
            first_day_of_week = 1,
            min_date_allowed = dt(2019,1,1),
            max_date_allowed = dt(2019,12,31),
            initial_visible_month = dt(2019,1,1),
            start_date = dt(2018, 12, 21),
            end_date = dt(2019,1,9),
        ), 
        className = 'flex flex-grow-1 items-center justify-center w-third ma0 '
    ),
    html.Div(children = [
        html.Div(
            dcc.Dropdown(
                id = 'metric-choice-r2',
                options = [{'label': "скв.", 'value': 'well'}, {'label': 'п.м.', 'value': 'meter'}],
                value = 'well',
                placeholder = 'Выберите метрику',
                className = 'flex pa0 w-100',
                style = {'minWidth': '8rem'},
            ), 
            className = 'flex flex-grow-1 items-center justify-center w-25 ma0'
        ),
        html.Div(
            dcc.Dropdown(
                id = 'area-choice-r2',
                options = [{'label': area, 'value': area} for area in areas_list],
                value = areas_list,
                multi = True,
                placeholder = 'Выберите участок',
                className = 'flex pa0 w-100',
                style = {'minWidth': '24rem'},
            ), 
            className = 'flex flex-grow-1 items-center justify-center w-75 ma0'
        )
    ], className = 'flex justify-around items-stretch h-auto w-two-thirds ma0'),
], className = 'flex justify-around items-stretch h-auto pl1 mt1 mr2')

dashboard_r2_profit_tree = html.Div(children = [
    html.Div(children = [
        html.H4('Операционная прибыль', style = {'backgroundColor': '#00FF00'}),
        dcc.Graph(id = 'operating-profit-r2', className = 'flex flex-auto', 
            figure = {
                'data': [go.Table(
                    header = dict(
                        values = ["Показатели", "Значения"],
                        fill = dict(color = 'grey'),
                        line = dict(color = '#506784'),
                        font = dict(color = 'white'),
                    ), 
                    cells = dict(
                        values = [
                            ["План", "Факт", "@Risk", "Турбо"],
                            [0, -202038, 0, 0]
                        ],
                        align = ['left', 'center'],
                        line = dict(color = '#506784'),
                        font = dict(color = ['white', 'black']),
                        fill = dict(color = ['#008000','#90EE90']),
                    )
                )],
                'layout': {
                    'margin': {'t': 0, 'r': 0, 'b': 0, 'l': 0}
                }
            }
        )
    ], className = 'css_cell w-25'),
    html.Div(children = [
        html.H4('Объем бурения', style = {'backgroundColor': '#1E90FF'}),
        dcc.Graph(id = 'total-volume-r2', className = 'flex flex-auto',
            figure = {
                'data': [go.Table(
                    header = dict(
                        values = ["Показатели", "Значения"],
                        fill = dict(color = 'grey'),
                        line = dict(color = '#506784'),
                        font = dict(color = 'white'),
                    ), 
                    cells = dict(
                        values = [
                            ["План (cкв.)", "Факт (cкв.)", "@Risk", "Турбо"],
                            [110, 108, 0, 0]
                        ],
                        align = ['left', 'center'],
                        line = dict(color = '#506784'),
                        font = dict(color = ['white', 'black']),
                        fill = dict(color = ['#4682B4','#ADD8E6']),
                    )
                )],
                'layout': {'margin': {'t': 0, 'r': 0, 'b': 0, 'l': 0}}
            }
        )
    ], className = 'css_cell w-25'),
    html.Div(children = [
        html.H4('Цена', style = {'backgroundColor': '#FFD700'}),
        dcc.Graph(id = 'average-price-r2', className = 'flex flex-auto h-auto',
            figure = {
                'data': [go.Table(
                    header = dict(
                        values = ["Показатели", "Значения"],
                        fill = dict(color = 'grey'),
                        line = dict(color = '#506784'),
                        font = dict(color = 'white'),
                    ), 
                    cells = dict(
                        values = [
                            ["A", "B", "C", "D"],
                            [0, 0, 0, 0]
                        ],
                        align = ['left', 'center'],
                        line = dict(color = '#506784'),
                        font = dict(color = ['white', 'black']),
                        fill = dict(color = ['#BDB76B','#FFFFE0']),
                    )
                )],
                'layout': {
                    'margin': {'t': 0, 'r': 0, 'b': 0, 'l': 0}
                }
            }
        )
    ], className = 'css_cell w-25'),
    html.Div(children = [
        html.H4('Расходы', style = {'backgroundColor': '#FF0000'}),
        dcc.Graph(id = 'total-expenses-r2', className = 'flex flex-auto h-auto', 
            figure = {
                'data': [go.Table(
                    header = dict(
                        values = ["Показатели", "Значения"],
                        fill = dict(color = 'grey'),
                        line = dict(color = '#506784'),
                        font = dict(color = 'white'),
                    ), 
                    cells = dict(
                        values = [
                            ["План", "Факт", "@Risk", "Турбо"],
                            [0, 0, 0, 0]
                        ],
                        align = ['left', 'center'],
                        line = dict(color = '#506784'),
                        font = dict(color = ['white', 'black']),
                        fill = dict(color = ['#B22222', '#E9967A'])
                    )
                )],
                'layout': {
                    'margin': {'t': 0, 'r': 0, 'b': 0, 'l': 0}
                }
            }
        )
    ], className = 'css_cell w-25')
], className = 'flex flex-auto justify-between pa1 h-auto', style = {'maxHeight': '20vh', 'minHeight': '9.5rem'})


dashboard_r2_table = html.Div(
    dcc.Graph(id = 'table-area-stat-r2', className = 'css_figure', config = {'displaylogo': False, 'showLink': False}),
    className = 'css_cell', style = {'maxHeight': '23rem'}
)

dashboard_r2_apq = html.Div(children = [
    html.Div(children = [
        html.H4('A: Доступность', style = {'backgroundColor': '#ffebae'}),
        dcc.Graph(id = 'A-r2', className = 'css_figure')
    ], className = 'css_cell', style = {'height': '33%'}),
    html.Div(children = [
        html.H4('P: Производительность', style = {'backgroundColor': '#77a7ae'}),
        dcc.Graph(id = 'P-r2', className = 'css_figure')
    ], className = 'css_cell', style = {'height': '33%'}),
    html.Div(children = [
        html.H4('Q: Качество', style = {'backgroundColor': '#ffadc1'}),
        dcc.Graph(id = 'Q-r2', className = 'css_figure')
    ], className = 'css_cell', style = {'height': '33%'})
], className = 'flex flex-grow-1 flex-column pa1 vh-100', style = {'maxHeight': '100vh'})


# FINAL LAYOUT
layout = html.Div([
    dashboard_r2_sliders,
    dcc.Markdown(children = '---'),
    dashboard_r2_profit_tree,
    dcc.Markdown(children = '---'),
    dashboard_r2_table,
    dcc.Markdown(children = '---'),
    dashboard_r2_apq
], className = 'flex flex-grow-1 flex-column', style = {'maxWidth': '85vw'})